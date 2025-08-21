from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from datetime import datetime
from typing import List, Dict
import logging

app = FastAPI(title="Storage Service", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoreRequest(BaseModel):
    results: List[Dict]
    timestamp: str

# Simple file-based storage (for MVP)
STORAGE_DIR = "/app/data"
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "💾 Stolen Bike Storage Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "storage"}

@app.post("/results")
async def store_results(request: StoreRequest):
    """Store search results"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.json"
        filepath = os.path.join(STORAGE_DIR, filename)
        
        data = {
            "timestamp": request.timestamp,
            "search_time": timestamp,
            "count": len(request.results),
            "results": request.results,
            "summary": {
                "total_ads": len(request.results),
                "high_relevance": len([r for r in request.results if r.get('relevance_score', 0) >= 5]),
                "posted_after_theft": len([r for r in request.results if r.get('posted_after_theft', False)]),
                "urls": [r['url'] for r in request.results]
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Stored {len(request.results)} results to {filename}")
        
        return {
            "status": "stored",
            "filename": filename,
            "count": len(request.results),
            "high_relevance_count": data['summary']['high_relevance'],
            "posted_after_theft_count": data['summary']['posted_after_theft']
        }
    except Exception as e:
        logger.error(f"❌ Failed to store results: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/results")
async def get_recent_results(limit: int = 10):
    """Get recent search results"""
    try:
        files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.json')]
        files.sort(reverse=True)  # Most recent first
        
        recent_results = []
        for filename in files[:limit]:
            filepath = os.path.join(STORAGE_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recent_results.append({
                        "filename": filename,
                        "timestamp": data.get("search_time"),
                        "count": data.get("count", 0),
                        "high_relevance": data.get("summary", {}).get("high_relevance", 0),
                        "posted_after_theft": data.get("summary", {}).get("posted_after_theft", 0)
                    })
            except Exception as e:
                logger.error(f"❌ Error reading {filename}: {e}")
                continue
        
        return {"recent_searches": recent_results}
    except Exception as e:
        logger.error(f"❌ Failed to get results: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/results/{filename}")
async def get_specific_result(filename: str):
    """Get specific search result file"""
    try:
        filepath = os.path.join(STORAGE_DIR, filename)
        
        if not os.path.exists(filepath):
            return {"status": "error", "error": "File not found"}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        logger.error(f"❌ Failed to get specific result: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/stats")
async def get_storage_stats():
    """Get storage statistics"""
    try:
        files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.json')]
        
        total_searches = len(files)
        total_results = 0
        total_high_relevance = 0
        total_after_theft = 0
        
        for filename in files:
            filepath = os.path.join(STORAGE_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_results += data.get("count", 0)
                    summary = data.get("summary", {})
                    total_high_relevance += summary.get("high_relevance", 0)
                    total_after_theft += summary.get("posted_after_theft", 0)
            except:
                continue
        
        return {
            "total_searches": total_searches,
            "total_results": total_results,
            "total_high_relevance": total_high_relevance,
            "total_after_theft": total_after_theft,
            "storage_directory": STORAGE_DIR
        }
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        return {"status": "error", "error": str(e)}

@app.delete("/results")
async def clear_old_results(keep_days: int = 30):
    """Clear old result files (older than keep_days)"""
    try:
        files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.json')]
        current_time = datetime.now()
        deleted_count = 0
        
        for filename in files:
            filepath = os.path.join(STORAGE_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            
            if (current_time - file_time).days > keep_days:
                os.remove(filepath)
                deleted_count += 1
                logger.info(f"🗑️ Deleted old file: {filename}")
        
        return {
            "status": "cleaned",
            "deleted_files": deleted_count,
            "remaining_files": len(files) - deleted_count
        }
    except Exception as e:
        logger.error(f"❌ Failed to clean old results: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
