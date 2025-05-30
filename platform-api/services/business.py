import asyncio
import os
import json
import logging
from ..db.postgres.connection import DatabaseConnectionManager
from ..dtos.business import CreateBusinessInputDto, CreateBusinessOutputDto, GetBusinessOutputDto, CreateRelationshipInputDto, CreateRelationshipOutputDto, GetRelationshipsOutputDto, RelationshipDto, DeleteRelationshipOutputDto, GetRelationshipOutputDto
from typing import List

class BusinessService:
    _instance = None
    _init_lock = asyncio.Lock()
    _initialized = False
    _database_manager = None
    _graph_name = os.getenv("DATABASE_GRAPH", "business_graph")
    
    async def __new__(cls):
        if cls._instance is None:
            async with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super(BusinessService, cls).__new__(cls)
                    await cls._initialize()
                    cls._initialized = True
        else:
            # Wait for initialization to complete if another task is initializing
            while not cls._initialized:
                await asyncio.sleep(0.01)
        return cls._instance
    
    @classmethod
    async def _initialize(cls):
        """Initialize the database connection"""
        cls._instance._database_manager = await DatabaseConnectionManager(cls._graph_name)
    
    @classmethod
    async def get(cls, business_id: str) -> GetBusinessOutputDto | None:
        service = await cls()
        result = await service._get_by_id(business_id)
        if not result:
            return None

        return result

    async def _get_by_id(self, business_id: str) -> dict | None:
        if not business_id:
            return None
        
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"""
                        SELECT * FROM {graph_name}.\"Business\" WHERE id = '{business_id}'
                        """
                    )

                    result = await cursor.fetchall()

                    if not result or len(result) == 0:
                        return None
                    
                    businessId = result[0][0]
                    businessDetails = json.loads(result[0][1])

                    return {    
                        "id": businessId,
                        "name": businessDetails["name"],
                        "category": businessDetails["category"]
                    }
            
            except Exception as ex:
                logging.error(type(ex), ex)
                return None

    @classmethod
    async def get_by_name_and_category(cls, name: str, category: str) -> GetBusinessOutputDto | None:
        service = await cls()
        result = await service._get_by_name_and_category(name, category)
        if not result:
            return None

        return result

    async def _get_by_name_and_category(self, name: str, category: str) -> dict | None:

        if not name or not category:
            return None
        
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name
            
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"""
                    SELECT * FROM {graph_name}.\"Business\" WHERE 
                    (ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text % '{name}' AND
                    ag_catalog.agtype_access_operator(properties, '"category"'::ag_catalog.agtype)::text % '{category}')
                    OR 
                    (similarity(ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text, '{name}') > 0.3 AND
                    similarity(ag_catalog.agtype_access_operator(properties, '"category"'::ag_catalog.agtype)::text, '{category}') > 0.3);
                    """)

                result = await cursor.fetchall()
                

                if not result or len(result) == 0:
                    return None
                
                entity = json.loads(result[0][1])

                return {
                    "id": str(result[0][0]),
                    "name": entity["name"],
                    "category": entity["category"]
                }
    
    async def _create(self, name: str, category: str) -> dict | None:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name
            
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f"SELECT * from cypher('{graph_name}', $$ CREATE (n:Business {{name: '{name}', category: '{category}'}}) RETURN n $$) as (node agtype);")

                    # Fetch the result
                    result = await cursor.fetchall()

                    # Get the string from the nested structure
                    data = json.loads(result[0][0].split('::vertex')[0])

                    return data
                
                except Exception as ex:
                    logging.error(type(ex), ex)
                    # if exception occurs, rollback the transaction
                    await conn.rollback()
                    return None
            
    @classmethod
    async def create(cls, input: CreateBusinessInputDto) -> CreateBusinessOutputDto | None:
        service = await cls()
        async with service._database_manager.get_connection() as conn:
            
            async with conn.cursor() as cursor:
                # Check if the business already exists
                business = await service._get_by_name_and_category(input.name, input.category)

                if business:
                    return {"id":str(business["id"])}
                
                # Create the business if it doesn't exist
                data = await service._create(input.name, input.category)
                if not data:
                    return None

                return {"id":str(data["id"])}
    

    async def _create_relationship(self, source_business_id: str, target_business_id: str, relationship_type: str, transaction_volume: int) -> dict | None:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f"""
                        SELECT * from cypher('{graph_name}', $$
                            MATCH (a:Business), (b:Business) 
                            WHERE id(a) = {source_business_id} AND id(b) = {target_business_id}
                            CREATE (a)-[r:BusinessRelationship {{
                                type: '{relationship_type}',
                                transaction_volume: {transaction_volume}
                            }}]->(b)
                            RETURN a, r, b
                        $$) as (source agtype, relationship agtype, target agtype);
                    """)

                    result = await cursor.fetchall()

                    if not result or len(result) == 0:
                        return None

                    # Get the second element (edge) from the first tuple in results
                    edge_data_str = result[0][1]
                    
                    # The data is a string in AGE format like: {"id": 1970324836974593, ...}::edge
                    # Extract the JSON part by removing the ::edge suffix
                    edge_data_str = edge_data_str.split('::edge')[0]
                    
                    # Parse the JSON
                    return json.loads(edge_data_str)

                except Exception as ex:
                    logging.error(type(ex), ex)
                    return None
    
    async def _get_relationship(self, source_business_id: str, target_business_id: str, relationship_type: str | None = None) -> dict | None:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            async with conn.cursor() as cursor:
                await cursor.execute(f"""
                    SELECT * from cypher('{graph_name}', $$
                        MATCH (a:Business)-[r:BusinessRelationship]->(b:Business)
                        WHERE id(a) = {source_business_id} AND id(b) = {target_business_id}
                        {f"AND r.type = '{relationship_type}'" if relationship_type else ""}
                        RETURN r
                    $$) as (relationship agtype);
                """)

                result = await cursor.fetchall()

                if not result or len(result) == 0:
                    return None

                return json.loads(result[0][0].split('::edge')[0])

    @classmethod
    async def create_relationship(cls, business_id: str, input: CreateRelationshipInputDto) -> CreateRelationshipOutputDto | None:
        service = await cls()

        source_business_id = await service._get_by_id(business_id)
        if not source_business_id:
            return None

        target_business = await service._get_by_id(input.business_id)
        if not target_business:
            return None
        
        # Check if the relationship already exists
        relationship = await service._get_relationship(source_business_id['id'], target_business['id'], input.relationship_type)
        if relationship:
           return {"id":str(relationship["id"])}
        
        relationship_type = input.relationship_type
        transaction_volume = input.transaction_volume

        result = await service._create_relationship(source_business_id['id'], target_business['id'], relationship_type, transaction_volume)
        if not result:
            return None

        return {"id":str(result["id"])}
    
    async def _get_relationships(self, business_id: str) -> List[RelationshipDto] | None:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            async with conn.cursor() as cursor:
                await cursor.execute(f"""
                    SELECT * from cypher('{graph_name}', $$
                        MATCH (a:Business)-[r:BusinessRelationship]->(b:Business)
                        WHERE id(a) = {business_id}
                        RETURN r.type as relationship_type, 
                            r.transaction_volume as volume,
                            id(b) as related_business_id,
                            b.name as related_business_name,
                            b.category as related_business_category
                    $$) as (relationship_type agtype, volume agtype, related_business_id agtype, related_business_name agtype, related_business_category agtype);
                """)

                result = await cursor.fetchall()

                if not result or len(result) == 0:
                    return None
            
                relationships = []
                for row in result:
                    relationships.append(RelationshipDto(
                        id=str(row[2]),
                        type=row[0].strip('"'),  # Remove the surrounding quotes
                        transaction_volume=int(row[1]),
                        name=row[3].strip('"'),  # Remove the surrounding quotes
                        category=row[4].strip('"')  # Remove the surrounding quotes
                    ))

                return relationships

    @classmethod
    async def get_relationships(cls, business_id: str) -> GetRelationshipsOutputDto | None:
        service = await cls()
        business = await service._get_by_id(business_id)
        if not business:
            return None

        relationships = await service._get_relationships(business['id'])
        if not relationships:
            return None

        return {
            "id": business['id'],
            "name": business['name'],
            "category": business['category'],
            "relationships": relationships
        }
    
    async def _delete_relationship(self, relationship_id: str) -> bool:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f"""
                        SELECT * from cypher('{graph_name}', $$
                            MATCH (a:Business)-[r:BusinessRelationship]->(b:Business)
                            WHERE id(r) = {relationship_id}
                            DELETE r
                            RETURN count(*) as deleted_count
                        $$) as (deleted_count agtype);
                    """)
                    result = await cursor.fetchone()
                    deleted_count = int(result[0]) if int(result[0]) > 0 else 0
                    return deleted_count > 0
                except Exception as ex:
                    logging.error(type(ex), ex)
                    return False    
    
    async def _get_relationship_by_id(self, relationship_id: str) -> dict | None:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            async with conn.cursor() as cursor:
                await cursor.execute(f"""
                    SELECT * from cypher('{graph_name}', $$
                        MATCH (a:Business)-[r:BusinessRelationship]->(b:Business)
                        WHERE id(r) = {relationship_id}
                        RETURN r, a, b
                    $$) as (relationship agtype, source_business agtype, target_business agtype);
                """)

                result = await cursor.fetchall()

                if not result or len(result) == 0:
                    return None

                return json.loads(result[0][0].split('::edge')[0])
                
    @classmethod
    async def delete_relationship(cls, relationship_id: str) -> DeleteRelationshipOutputDto | None:
        service = await cls()
        relationship = await service._get_relationship_by_id(relationship_id)
        if not relationship:
            return None

        result = await service._delete_relationship(relationship['id'])
        return {"done": result}
    
    async def _get_indirect_relationship_shortest_path(self, source_business_id: str, target_business_id: str, based_on_max_transaction_volume: bool = False) -> dict | None:
        async with self._database_manager.get_connection() as conn:
            graph_name = self._graph_name

            async with conn.cursor() as cursor:
                # 1) Find all paths from source to target
                # await cursor.execute(f"""
                #     SELECT * from cypher('{graph_name}', $$
                #         MATCH path = (a:Business)-[r:BusinessRelationship*1..1000000]-(b:Business)
                #         WHERE id(a) = {source_business_id} AND id(b) = {target_business_id}
                #         RETURN path, length(path) as path_length
                #     $$) as (path agtype, path_length agtype)
                #     ORDER BY path_length
                #     LIMIT 1;
                # """)

                # TODO: We should first try this indirect search with a max of 200 hops
                # If we don't find a path, we should push this request to a background job queue (AWS SQS)
                # The background job should try to find a path with a max of 1,000,000 hops
                if based_on_max_transaction_volume:

                    # 2) Find the path with maximum transaction volume from source to target
                    # We are are considering transaction volume here (maximum transaction volume) between the source and target
                    # So rather than finding the shortest path (fewest hops), it's finding the path 
                    # with the maximum cumulative transaction volume between the source and target businesses, regardless of how many hops that path contains.
                    # From 1 to 1,000,000 hops
                    await cursor.execute(f"""
                        SELECT * from cypher('{graph_name}', $$
                            MATCH path = (a:Business)-[r:BusinessRelationship*1..1000000]-(b:Business)
                            WHERE id(a) = {source_business_id} AND id(b) = {target_business_id}
                            UNWIND relationships(path) AS rel
                            WITH path, length(path) AS path_length, sum(rel.transaction_volume) AS total_weight
                            WITH path, path_length, total_weight
                            ORDER BY total_weight DESC
                            LIMIT 1
                            UNWIND nodes(path) AS node
                            RETURN collect(node.name) AS business_names, path_length, total_weight AS transaction_volume
                        $$) as (business_names agtype, path_length agtype, transaction_volume agtype);
                    """)
                else:
                    # TODO: We should first try this indirect search with a max of 200 hops
                    # If we don't find a path, we should push this request to a background job queue (AWS SQS)
                    # The background job should try to find a path with a max of 1,000,000 hops

                    # 3) Find the shortest path from source to target (e.g., Djikstra's algorithm)
                    # This finds all paths between source and target businesses, orders them by path length (number of hops), 
                    # and returns the shortest one which is effectively what Dijkstra's algorithm would do when all edge weights are equal.
                    # We are not considering transaction volume here, the weight is 1 for all relationships
                    # From 1 to 1,000,000 hops
                    await cursor.execute(f"""
                        SELECT * from cypher('{graph_name}', $$
                            MATCH path = (a:Business)-[r:BusinessRelationship*1..1000000]-(b:Business)
                            WHERE id(a) = {source_business_id} AND id(b) = {target_business_id}
                            WITH path
                            ORDER BY length(path)
                            LIMIT 1
                            UNWIND nodes(path) AS node
                            RETURN collect(node.name) AS business_names, length(path) AS path_length
                        $$) as (business_names agtype, path_length agtype);
                    """)


                result = await cursor.fetchall()

                if not result or len(result) == 0:
                    return None

                return {
                    "distance_in_hops": int(result[0][1]),
                    "business_names": json.loads(result[0][0])
                }
                
    @classmethod
    async def get_relationship(cls, source_business_id: str, target_business_id: str, based_on_max_transaction_volume: bool = False) -> GetRelationshipOutputDto | None:
        service = await cls()
        relationship = await service._get_relationship(source_business_id, target_business_id)
        # We found a direct relationship
        if relationship:
            return {
                "distance_in_hops": 1,
                "relationship_type": relationship['properties']['type'],
                "transaction_volume": relationship['properties']['transaction_volume']
            }

        indirect_relationship = await service._get_indirect_relationship_shortest_path(source_business_id, target_business_id, based_on_max_transaction_volume)

        if not indirect_relationship:
            return None

        return {
            "distance_in_hops": indirect_relationship['distance_in_hops'],
            "business_names": "->".join(indirect_relationship['business_names'])
        }
