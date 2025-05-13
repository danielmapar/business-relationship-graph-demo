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
COMPANY_COUNT = 1000
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
async def create_company(session, index):
    try:
        unique_id = str(uuid.uuid4())
        company = {
            "name": f"Company{index}-{unique_id}",
            "category": "Technology"
        }
        
        logger.info(f"Creating company {index}: {company['name']}")
        
        async with session.post(f"{BASE_URL}/businesses", json=company, timeout=REQUEST_TIMEOUT) as response:
            if response.status != 200 and response.status != 201:
                text = await response.text()
                logger.error(f"Failed to create company {index}, status: {response.status}, response: {text}")
                return None
            
            data = await response.json()
            logger.info(f"Successfully created company {index}: {data['id']}")
            return data
    except Exception as e:
        logger.error(f"Failed to create company {index}: {str(e)}")
        return None

# Create a relationship between companies (prev -> next)
async def create_relationship(session, prev_id, next_id):
    try:
        relationship = {
            "businessId": next_id,
            "relationshipType": "vendor",
            "transactionVolume": 100
        }
        
        logger.info(f"Creating relationship: Company with ID {prev_id} -> Company with ID {next_id}")
        
        async with session.post(
            f"{BASE_URL}/businesses/{prev_id}/relationships", 
            json=relationship,
            timeout=REQUEST_TIMEOUT
        ) as response:
            if response.status != 200 and response.status != 201:
                text = await response.text()
                logger.error(f"Failed to create relationship, status: {response.status}, response: {text}")
                return None
            
            data = await response.json()
            logger.info(f"Successfully created relationship with ID: {data['id']}")
            return data
    except Exception as e:
        logger.error(f"Failed to create relationship: {str(e)}")
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

# Main function to create the linked list of companies
async def create_company_chain():
    logger.info(f"Starting creation of {COMPANY_COUNT} companies in a linked list chain")
    start_time = time.time()
    
    # Check API health first
    if not await check_api_health():
        logger.error("API server is not reachable. Exiting.")
        return

    companies = []
    
    # Create session for all requests
    async with aiohttp.ClientSession() as session:
        # Step 1: Create all companies
        for i in range(1, COMPANY_COUNT + 1):
            company = await create_company(session, i)
            if company:
                companies.append(company)
            else:
                logger.error(f"Failed to create company {i}. Exiting.")
                return
        
        # Step 2: Link companies in a chain
        logger.info(f"Creating relationships to form a linked list chain")
        for i in range(len(companies) - 1):
            current_company = companies[i]
            next_company = companies[i+1]
            
            relationship = await create_relationship(
                session, 
                current_company['id'], 
                next_company['id']
            )
            
            if not relationship:
                logger.error(f"Failed to create relationship between companies {i+1} and {i+2}. Continuing...")
    
    duration = time.time() - start_time
    logger.info(f"Company chain creation completed in {duration:.2f} seconds")
    logger.info(f"Created {len(companies)} companies with {len(companies)-1} relationships")
    logger.info(f"First company: {companies[0]['id']}")
    logger.info(f"Last company: {companies[-1]['id']}")
    logger.info(f"Number of hops from first to last: {len(companies)-1}")

# Entry point
if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting script at {start_time}")
    
    asyncio.run(create_company_chain())
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Script completed at {end_time}")
    logger.info(f"Total duration: {duration:.2f} seconds")