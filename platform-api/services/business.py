import asyncio
import os
from ..db.postgres.connection import DatabaseConnectionManager

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
    async def create(cls):
        service = await cls()
        async with service._database_manager.get_connection() as conn:
            graph_name = service._graph_name
            
            async with conn.cursor() as cursor:
                try:
                    # Create Person nodes
                    await cursor.execute(f"SELECT * from cypher('{graph_name}', $$ CREATE (n:Person {{name: 'Joe', title: 'Developer'}}) $$) as (v agtype);")

                    # When data inserted or updated, commit the transaction
                    await conn.commit()
                    return {"business": True}
                    
                except Exception as ex:
                    print(type(ex), ex)
                    # if exception occurs, rollback the transaction
                    await conn.rollback()
                    return {"error": str(ex)}