import asyncio
import aiohttp
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime

# Configuration
HOST = os.environ.get('API_HOST', 'localhost:8080')
RELATIONSHIP_COUNT = 100
LOG_FILE = 'data-generation.log'
REQUEST_TIMEOUT = 10

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = f"http://{HOST}"

# Create a company
async def create_company(session, name="Main Company", category="Technology"):
    try:
        unique_id = str(uuid.uuid4())
        company = {
            "name": f"{name}-{unique_id}",
            "category": category
        }
        
        logger.info(f"Creating main company: {company['name']}")
        
        async with session.post(f"{BASE_URL}/businesses", json=company, timeout=REQUEST_TIMEOUT) as response:
            if response.status != 200 and response.status != 201:
                text = await response.text()
                logger.error(f"Failed to create main company, status: {response.status}, response: {text}")
                return None
            
            data = await response.json()
            logger.info(f"Successfully created main company with ID: {data['id']}")
            return data
    except Exception as e:
        logger.error(f"Failed to create main company: {str(e)}")
        return None

# Create a related company
async def create_related_company(session, index):
    try:
        unique_id = str(uuid.uuid4())
        company = {
            "name": f"Related Company {index}-{unique_id}",
            "category": "Technology"
        }
        
        logger.info(f"Creating related company {index}: {company['name']}")
        
        async with session.post(f"{BASE_URL}/businesses", json=company, timeout=REQUEST_TIMEOUT) as response:
            if response.status != 200 and response.status != 201:
                text = await response.text()
                logger.error(f"Failed to create related company {index}, status: {response.status}, response: {text}")
                return None
            
            data = await response.json()
            logger.info(f"Successfully created related company {index} with ID: {data['id']}")
            return data
    except Exception as e:
        logger.error(f"Failed to create related company {index}: {str(e)}")
        return None

# Create a relationship between companies
async def create_relationship(session, main_id, related_id, index):
    try:
        relationship = {
            "businessId": related_id,
            "relationshipType": "vendor",
            "transactionVolume": 100 * index  # Varying transaction volume
        }
        
        logger.info(f"Creating relationship {index}: Main company -> Related company {index}")
        
        async with session.post(
            f"{BASE_URL}/businesses/{main_id}/relationships", 
            json=relationship,
            timeout=REQUEST_TIMEOUT
        ) as response:
            if response.status != 200 and response.status != 201:
                text = await response.text()
                logger.error(f"Failed to create relationship {index}, status: {response.status}, response: {text}")
                return None
            
            data = await response.json()
            logger.info(f"Successfully created relationship {index} with ID: {data['id']}")
            return data
    except Exception as e:
        logger.error(f"Failed to create relationship {index}: {str(e)}")
        return None

# Check API server health
async def check_api_health():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}", timeout=5) as response:
                if response.status == 200:
                    logger.info(f"API server at {BASE_URL} is reachable")
                    return True
                else:
                    logger.error(f"API server returned status {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Failed to connect to API server at {BASE_URL}: {str(e)}")
        return False

# Main function to create a company with relationships
async def create_company_with_relationships():
    logger.info(f"Starting creation of 1 main company with {RELATIONSHIP_COUNT} relationships")
    start_time = time.time()
    
    # Check API health first
    if not await check_api_health():
        logger.error("API server is not reachable. Exiting.")
        return

    # Create session for all requests
    async with aiohttp.ClientSession() as session:
        # Step 1: Create the main company
        main_company = await create_company(session)
        if not main_company:
            logger.error("Failed to create main company. Exiting.")
            return
        
        main_id = main_company['id']
        logger.info(f"Main company created with ID: {main_id}")
        
        # Step 2: Create related companies and relationships
        for i in range(1, RELATIONSHIP_COUNT + 1):
            # Create a related company
            related_company = await create_related_company(session, i)
            if not related_company:
                logger.error(f"Failed to create related company {i}. Skipping.")
                continue
            
            related_id = related_company['id']
            
            # Create relationship between main company and related company
            relationship = await create_relationship(session, main_id, related_id, i)
            if not relationship:
                logger.error(f"Failed to create relationship {i}. Continuing...")
    
    duration = time.time() - start_time
    logger.info(f"Company creation with relationships completed in {duration:.2f} seconds")
    logger.info(f"Created 1 main company with up to {RELATIONSHIP_COUNT} relationships")
    logger.info(f"Main company ID: {main_id}")

# Entry point
if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting script at {start_time}")
    
    asyncio.run(create_company_with_relationships())
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Script completed at {end_time}")
    logger.info(f"Total duration: {duration:.2f} seconds")