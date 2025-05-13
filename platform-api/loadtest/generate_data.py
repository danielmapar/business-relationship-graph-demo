import asyncio
import aiohttp
import json
import random
import time
import os
import logging
import sys
from datetime import datetime

# Configuration
HOST = os.environ.get('API_HOST', 'localhost:8080')
BUSINESS_COUNT = int(os.environ.get('BUSINESS_COUNT', '1000000'))
RELATIONSHIPS_PER_BUSINESS = int(os.environ.get('RELATIONSHIPS_PER_BUSINESS', '100'))
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '50'))
MAX_CONCURRENT_REQUESTS = int(os.environ.get('MAX_CONCURRENT_REQUESTS', '10'))
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))
LOG_FILE = 'data-generation.log'
# Add option to skip phases
SKIP_BUSINESSES = os.environ.get('SKIP_BUSINESSES', 'false').lower() == 'true'
SKIP_RELATIONSHIPS = os.environ.get('SKIP_RELATIONSHIPS', 'false').lower() == 'true'
# Add option to save/load businesses
BUSINESSES_FILE = os.environ.get('BUSINESSES_FILE', 'businesses.json')

# Categories for random business generation
CATEGORIES = [
    'Technology', 'Retail', 'Manufacturing', 'Healthcare', 'Financial',
    'Education', 'Food', 'Hospitality', 'Entertainment', 'Automobiles',
    'Construction', 'Real Estate', 'Transportation', 'Energy', 'Agriculture'
]

# Relationship types
RELATIONSHIP_TYPES = ['vendor', 'client']

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = f"http://{HOST}"

# Generate a random business name
def generate_business_name(index):
    prefixes = ['Advanced', 'Global', 'Premier', 'Elite', 'Peak', 'Next', 'Future', 'Smart', 'Digital', 'Innovative']
    suffixes = ['Solutions', 'Systems', 'Enterprises', 'Tech', 'Group', 'Inc', 'LLC', 'Partners', 'Services', 'Industries']
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f"{prefix} {suffix} {index}"

# Generate random transaction volume
def generate_transaction_volume():
    return random.randint(100, 10100)

# Create a business
async def create_business(session, index):
    try:
        business = {
            "name": generate_business_name(index),
            "category": random.choice(CATEGORIES)
        }
        
        logger.debug(f"Sending request to create business {index}: {json.dumps(business)}")
        start_time = time.time()
        
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with session.post(f"{BASE_URL}/businesses", json=business, timeout=timeout) as response:
            elapsed = time.time() - start_time
            status = response.status
            logger.debug(f"Response for business {index}: status={status}, time={elapsed:.2f}s")
            
            if status != 200 and status != 201:
                text = await response.text()
                logger.error(f"Failed to create business {index}, status: {status}, response: {text}")
                return None
            
            data = await response.json()
            logger.debug(f"Successfully created business {index}: {data}")
            return data
    except asyncio.TimeoutError:
        logger.error(f"Timeout creating business {index} after {REQUEST_TIMEOUT} seconds")
        return None
    except Exception as e:
        logger.error(f"Failed to create business {index}: {str(e)}", exc_info=True)
        return None

# Create a relationship between businesses
async def create_relationship(session, business_id, other_business_id):
    try:
        relationship = {
            "businessId": other_business_id,
            "relationshipType": random.choice(RELATIONSHIP_TYPES),
            "transactionVolume": generate_transaction_volume()
        }
        
        logger.debug(f"Sending request to create relationship between {business_id} and {other_business_id}")
        start_time = time.time()
        
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with session.post(
            f"{BASE_URL}/businesses/{business_id}/relationships", 
            json=relationship,
            timeout=timeout
        ) as response:
            elapsed = time.time() - start_time
            status = response.status
            logger.debug(f"Response for relationship between {business_id} and {other_business_id}: status={status}, time={elapsed:.2f}s")
            
            if status != 200 and status != 201:
                text = await response.text()
                logger.error(f"Failed to create relationship, status: {status}, response: {text}")
                return None
            
            data = await response.json()
            return data
    except asyncio.TimeoutError:
        logger.error(f"Timeout creating relationship between {business_id} and {other_business_id} after {REQUEST_TIMEOUT} seconds")
        return None
    except Exception as e:
        logger.error(f"Failed to create relationship between {business_id} and {other_business_id}: {str(e)}", exc_info=True)
        return None

# Check API server health
async def check_api_health():
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{BASE_URL}") as response:
                if response.status == 200:
                    logger.info(f"API server at {BASE_URL} is reachable and returned status 200")
                    return True
                else:
                    logger.error(f"API server returned status {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Failed to connect to API server at {BASE_URL}: {str(e)}")
        return False

# Create a batch of businesses with retries
async def create_businesses_batch(session, start_index, count, max_retries=3):
    results = []
    for i in range(start_index, start_index + count):
        if i >= BUSINESS_COUNT:
            break
            
        retry_count = 0
        result = None
        
        while retry_count < max_retries and result is None:
            if retry_count > 0:
                logger.info(f"Retrying business {i} (attempt {retry_count+1}/{max_retries})")
                await asyncio.sleep(1)
                
            result = await create_business(session, i)
            retry_count += 1
            
        if result is not None:
            results.append(result)
            
    return results

# Create all businesses
async def create_all_businesses():
    logger.info(f"Starting business creation phase: {BUSINESS_COUNT} businesses")
    
    start_time = time.time()
    all_businesses = []
    
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT * 2)
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for batch_start in range(0, BUSINESS_COUNT, BATCH_SIZE):
                batch_start_time = time.time()
                
                batch_end = min(batch_start + BATCH_SIZE, BUSINESS_COUNT)
                logger.info(f"Creating businesses {batch_start} to {batch_end - 1}")
                
                # Create businesses in smaller chunks
                chunk_size = min(MAX_CONCURRENT_REQUESTS, BATCH_SIZE)
                batch_businesses = []
                
                for chunk_start in range(batch_start, batch_end, chunk_size):
                    chunk_count = min(chunk_size, batch_end - chunk_start)
                    logger.info(f"Processing chunk {chunk_start} to {chunk_start + chunk_count - 1}")
                    
                    chunk_results = await create_businesses_batch(session, chunk_start, chunk_count)
                    
                    for result in chunk_results:
                        batch_businesses.append(result)
                        all_businesses.append(result)
                        
                    # Save progress after each chunk
                    with open(BUSINESSES_FILE, 'w') as f:
                        json.dump(all_businesses, f)
                    
                    # Small delay between chunks
                    if chunk_start + chunk_size < batch_end:
                        await asyncio.sleep(0.5)
                
                batch_duration = time.time() - batch_start_time
                businesses_created = len(batch_businesses)
                logger.info(f"Created {businesses_created} businesses in batch. Total: {len(all_businesses)}/{BUSINESS_COUNT}")
                logger.info(f"Batch completed in {batch_duration:.2f} seconds")
                
                # Adaptive delay between batches
                #if batch_start + BATCH_SIZE < BUSINESS_COUNT:
                #    delay = max(1.0, min(5.0, 10.0 / (batch_duration + 0.1)))
                #    logger.info(f"Waiting {delay:.2f} seconds before next batch")
                #    await asyncio.sleep(delay)
        
        duration = time.time() - start_time
        logger.info(f"Business creation completed in {duration:.2f} seconds")
        logger.info(f"Total businesses created: {len(all_businesses)}")
        
        return all_businesses
    except Exception as e:
        logger.error(f"Business creation failed: {str(e)}", exc_info=True)
        duration = time.time() - start_time
        logger.info(f"Ran for {duration:.2f} seconds, created {len(all_businesses)} businesses")
        
        # Save what we have so far
        with open(BUSINESSES_FILE, 'w') as f:
            json.dump(all_businesses, f)
        
        return all_businesses

# Create relationships for all businesses
async def create_all_relationships(businesses):
    if len(businesses) == 0:
        logger.error("No businesses available to create relationships")
        return
    
    logger.info(f"Starting relationship creation phase for {len(businesses)} businesses")
    logger.info(f"Each business will have up to {RELATIONSHIPS_PER_BUSINESS} relationships")
    
    start_time = time.time()
    total_relationships = 0
    
    try:
        # Maximum number of businesses to process in one batch for relationships
        relationship_batch_size = min(100, len(businesses))
        
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT * 2)
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for batch_index in range(0, len(businesses), relationship_batch_size):
                batch_start_time = time.time()
                
                batch_end = min(batch_index + relationship_batch_size, len(businesses))
                batch_businesses = businesses[batch_index:batch_end]
                
                logger.info(f"Creating relationships for businesses {batch_index} to {batch_end - 1}")
                
                batch_relationships = 0
                
                for i, business in enumerate(batch_businesses):
                    max_relationships = min(RELATIONSHIPS_PER_BUSINESS, 10)  # Start with fewer relationships per business
                    business_relationships = 0
                    
                    # Create pool of potential relationship targets (excluding current business)
                    potential_targets = [b for b in businesses if b['id'] != business['id']]
                    
                    # If not enough businesses, adjust the number of relationships
                    max_relationships = min(max_relationships, len(potential_targets))
                    
                    # Randomly select businesses for relationships
                    if max_relationships > 0:
                        targets = random.sample(potential_targets, max_relationships)
                        
                        # Create relationships in parallel
                        async def create_with_retry(target):
                            for attempt in range(3):  # Try up to 3 times
                                result = await create_relationship(session, business['id'], target['id'])
                                if result is not None:
                                    return 1
                                await asyncio.sleep(1)  # Wait before retry
                            return 0
                        
                        tasks = [create_with_retry(target) for target in targets]
                        results = await asyncio.gather(*tasks)
                        
                        business_relationships = sum(results)
                        batch_relationships += business_relationships
                        total_relationships += business_relationships
                    
                    logger.info(f"Created {business_relationships} relationships for business {i + batch_index}")
                    
                    # Occasional delay to avoid overwhelming the server
                    if (i + 1) % 5 == 0:
                        await asyncio.sleep(0.5)
                
                batch_duration = time.time() - batch_start_time
                logger.info(f"Created {batch_relationships} relationships in batch. Total: {total_relationships}")
                logger.info(f"Batch completed in {batch_duration:.2f} seconds")
                
                # Adaptive delay between batches
                if batch_index + relationship_batch_size < len(businesses):
                    delay = max(1.0, min(5.0, 10.0 / (batch_duration + 0.1)))
                    logger.info(f"Waiting {delay:.2f} seconds before next batch")
                    await asyncio.sleep(delay)
        
        duration = time.time() - start_time
        logger.info(f"Relationship creation completed in {duration:.2f} seconds")
        logger.info(f"Total relationships created: {total_relationships}")
    except Exception as e:
        logger.error(f"Relationship creation failed: {str(e)}", exc_info=True)
        duration = time.time() - start_time
        logger.info(f"Ran for {duration:.2f} seconds, created {total_relationships} relationships")

# Main execution function
async def main():
    logger.info(f"Starting data generation with the following parameters:")
    logger.info(f"API_HOST: {HOST}")
    logger.info(f"BUSINESS_COUNT: {BUSINESS_COUNT}")
    logger.info(f"RELATIONSHIPS_PER_BUSINESS: {RELATIONSHIPS_PER_BUSINESS}")
    logger.info(f"BATCH_SIZE: {BATCH_SIZE}")
    logger.info(f"MAX_CONCURRENT_REQUESTS: {MAX_CONCURRENT_REQUESTS}")
    logger.info(f"REQUEST_TIMEOUT: {REQUEST_TIMEOUT}s")
    logger.info(f"SKIP_BUSINESSES: {SKIP_BUSINESSES}")
    logger.info(f"SKIP_RELATIONSHIPS: {SKIP_RELATIONSHIPS}")
    logger.info(f"BUSINESSES_FILE: {BUSINESSES_FILE}")
    
    # Check API health before starting
    is_healthy = await check_api_health()
    if not is_healthy:
        logger.error(f"API server at {BASE_URL} is not available. Exiting.")
        return
    
    businesses = []
    
    # Phase 1: Create businesses (or load from file if skipping)
    if SKIP_BUSINESSES:
        logger.info(f"Skipping business creation phase")
        try:
            with open(BUSINESSES_FILE, 'r') as f:
                businesses = json.load(f)
            logger.info(f"Loaded {len(businesses)} businesses from {BUSINESSES_FILE}")
        except FileNotFoundError:
            logger.error(f"Businesses file {BUSINESSES_FILE} not found!")
            return
        except json.JSONDecodeError:
            logger.error(f"Error decoding businesses file {BUSINESSES_FILE}")
            return
    else:
        businesses = await create_all_businesses()
    
    # Phase 2: Create relationships
    if not SKIP_RELATIONSHIPS:
        await create_all_relationships(businesses)
    else:
        logger.info(f"Skipping relationship creation phase")
    
    logger.info("Data generation process completed")

if __name__ == "__main__":
    # Set up event loop policy for Windows if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the main async function
    asyncio.run(main())