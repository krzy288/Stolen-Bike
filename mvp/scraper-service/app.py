from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import requests
import json
from scraper import StolenBikeScraper
from typing import List
import logging

app = FastAPI(title="Bike Scraper Service", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BikeConfig(BaseModel):
    brand: str = "Rockrider"
    model: str = "EXPL 500"
    color: str = "black"
    min_price: int = 400
    max_price: int = 2500
    theft_date: str = "2025-08-13"
    locations: List[str] = ["warszawa", "piaseczno", "pruszkow", "legionowo", "otwock"]

class SearchRequest(BaseModel):
    config: BikeConfig
    mode: str = "quick"  # quick, full

# Services URLs
STORAGE_SERVICE_URL = "http://storage-service:8000"

@app.get("/")
async def root():
    return {"message": "🚴 Stolen Bike Scraper Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scraper"}

@app.post("/search")
async def search_bikes(request: SearchRequest, background_tasks: BackgroundTasks):
    """Start bike search"""
    logger.info(f"Starting bike search in {request.mode} mode")
    
    # Run search in background
    background_tasks.add_task(run_search, request.config, request.mode)
    
    return {"message": "Search started", "mode": request.mode, "config": request.config.dict()}

@app.get("/search/auto")
async def auto_search(background_tasks: BackgroundTasks):
    """Auto search with default config (for cron jobs)"""
    config = BikeConfig()
    background_tasks.add_task(run_search, config, "quick")
    return {"message": "Auto search started", "config": config.dict()}

async def run_search(config: BikeConfig, mode: str):
    """Run the actual search"""
    try:
        logger.info(f"🔍 Starting {mode} search for {config.brand} {config.model}")
        scraper = StolenBikeScraper(config)
        results = scraper.search(mode)
        
        logger.info(f"🔍 Search completed. Found {len(results)} results")
        
        # Store results
        await store_results(results)
        
        # Simple console notification when bikes found
        if results:
            print(f"\n🚨 ALERT: Found {len(results)} potential matches!")
            print("=" * 60)
            for i, result in enumerate(results[:3], 1):  # Show top 3
                print(f"{i}. {result['title']}")
                print(f"   💰 {result['price']}")
                print(f"   📍 {result.get('location_date', 'Unknown')}")
                print(f"   � {result['url']}")
                print(f"   ⭐ Score: {result.get('relevance_score', 0)}/10")
                print("-" * 50)
            print(f"📊 Total matches: {len(results)}")
            print("🔍 Check the URLs above immediately!")
            print("=" * 60)
            logger.info(f"🚨 ALERT: {len(results)} potential matches found!")
        else:
            print(f"✅ No suspicious ads found - your bike hasn't appeared yet")
            logger.info("✅ No suspicious ads found - good news!")
            
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")

async def store_results(results):
    """Store results in storage service"""
    try:
        response = requests.post(
            f"{STORAGE_SERVICE_URL}/results",
            json={"results": results, "timestamp": "2025-08-21"},
            timeout=30
        )
        response.raise_for_status()
        logger.info("💾 Results stored successfully")
    except Exception as e:
        logger.error(f"❌ Failed to store results: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
