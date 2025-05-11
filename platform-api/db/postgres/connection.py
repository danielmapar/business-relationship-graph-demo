import os
import asyncio
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

class DatabaseConnectionManager:
    _instance = None
    _pool = None
    _init_lock = asyncio.Lock()
    _initialized = False

    async def __new__(cls, graph_name=None):   
        if cls._instance is None:
            async with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnectionManager, cls).__new__(cls)
                    await cls._initialize_connection_pool(graph_name)
                    cls._initialized = True
        else:
            # Wait for initialization to complete if another task is initializing
            while not cls._initialized:
                await asyncio.sleep(0.01)
        return cls._instance
    
    @classmethod
    def get_conn_string(self):
        return f"host={os.getenv('DATABASE_HOST', 'database')} port={os.getenv('DATABASE_PORT', '5432')} dbname={os.getenv('DATABASE_NAME', 'platform_api_db')} user={os.getenv('DATABASE_USER', 'intuit')} password={os.getenv('DATABASE_PASSWORD', 'password')}"

    @classmethod
    async def _initialize_connection_pool(cls, graph_name):
        """Initialize the async database connection pool"""
        conn_string = cls.get_conn_string()
        # Create the pool without opening it in the constructor
        cls._pool = AsyncConnectionPool(conn_string, min_size=1, max_size=10, open=False)
        # Explicitly open the pool
        await cls._pool.open()
        # Make sure we create the graph if it doesn't exist
        async with cls._pool.connection() as conn:
            async with conn.cursor() as cursor:
                # Load the AGE extension
                await cursor.execute("LOAD 'age';")
                # Set search path
                await cursor.execute("SET search_path = ag_catalog, \"$user\", public;")
                # Check if graph exists and create it if it doesn't
                await cursor.execute("SELECT * FROM ag_catalog.ag_graph WHERE name = %s;", [graph_name])
                result = await cursor.fetchall()
                if not result:
                    await cursor.execute("SELECT create_graph(%s);", [graph_name])
                    await conn.commit()
                    print(f"Graph '{graph_name}' created")
            
        print("Async database connection pool initialized")
        
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        conn = await self._pool.getconn()
        try:
            async with conn.cursor() as cursor:
                # Load the AGE extension
                await cursor.execute("LOAD 'age';")
                # Set search path
                await cursor.execute("SET search_path = ag_catalog, \"$user\", public;")
            yield conn
        finally:
            await self._pool.putconn(conn)
