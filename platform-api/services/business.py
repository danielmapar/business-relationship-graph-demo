import asyncio
import os
import json
import logging
from ..db.postgres.connection import DatabaseConnectionManager
from ..dtos.business import CreateBusinessInputDto, CreateBusinessOutputDto, GetBusinessOutputDto, CreateRelationshipInputDto, CreateRelationshipOutputDto

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

                # Get the string from the nested structure
                return json.loads(result[0][0].split('::vertex')[0])
    
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
                business_id = await service._get_by_name_and_category(input.name, input.category)

                if business_id:
                    return {"id":str(business_id)}
                
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
                            CREATE (a)-[r:{relationship_type} {{transaction_volume: {transaction_volume}}}]->(b)
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

    @classmethod
    async def create_relationship(cls, business_id: str, input: CreateRelationshipInputDto) -> CreateRelationshipOutputDto | None:
        service = await cls()

        source_business_id = await service._get_by_id(business_id)
        if not source_business_id:
            return None

        target_business = await service._get_by_id(input.business_id)
        if not target_business:
            return None
        
        relationship_type = input.relationship_type
        transaction_volume = input.transaction_volume

        result = await service._create_relationship(source_business_id['id'], target_business['id'], relationship_type, transaction_volume)
        if not result:
            return None

        return {"id":str(result["id"])}

