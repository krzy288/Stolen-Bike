#!/bin/bash

# Stolen Bike Finder MVP - Utility Scripts

echo "🚴 Stolen Bike Finder MVP - Management Script"
echo "=============================================="

case "$1" in
    "start")
        echo "🚀 Starting all services..."
        docker-compose up -d
        sleep 5
        echo "✅ Services started! Checking health..."
        curl -s http://localhost:8001/health && echo " ✅ Scraper Service"
        curl -s http://localhost:8002/health && echo " ✅ Notification Service"  
        curl -s http://localhost:8003/health && echo " ✅ Storage Service"
        ;;
    "stop")
        echo "🛑 Stopping all services..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Restarting all services..."
        docker-compose down
        docker-compose up -d
        ;;
    "build")
        echo "🏗️ Rebuilding all services..."
        docker-compose down
        docker-compose up --build -d
        ;;
    "logs")
        if [ -z "$2" ]; then
            echo "📋 Showing logs for all services..."
            docker-compose logs -f
        else
            echo "📋 Showing logs for $2..."
            docker-compose logs -f "$2"
        fi
        ;;
    "search")
        echo "🔍 Starting quick search..."
        curl -X GET "http://localhost:8001/search/auto"
        ;;
    "test")
        echo "🧪 Testing all services..."
        echo "Testing scraper service..."
        curl -s http://localhost:8001/health
        echo -e "\nTesting notification service..."
        curl -s http://localhost:8002/health
        echo -e "\nTesting storage service..."
        curl -s http://localhost:8003/health
        echo -e "\nTesting notification..."
        curl -X POST http://localhost:8002/test
        ;;
    "status")
        echo "📊 Service Status:"
        echo "=================="
        echo -n "Scraper Service: "
        curl -s http://localhost:8001/health > /dev/null && echo "✅ Running" || echo "❌ Down"
        echo -n "Notification Service: "
        curl -s http://localhost:8002/health > /dev/null && echo "✅ Running" || echo "❌ Down"
        echo -n "Storage Service: "
        curl -s http://localhost:8003/health > /dev/null && echo "✅ Running" || echo "❌ Down"
        
        echo -e "\n📈 Storage Stats:"
        curl -s http://localhost:8003/stats | python -m json.tool 2>/dev/null || echo "❌ Cannot retrieve stats"
        ;;
    "results")
        echo "📊 Recent Search Results:"
        curl -s http://localhost:8003/results | python -m json.tool
        ;;
    "clean")
        echo "🧹 Cleaning old results (keeping last 30 days)..."
        curl -X DELETE "http://localhost:8003/results?keep_days=30"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|build|logs [service]|search|test|status|results|clean}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"  
        echo "  restart  - Restart all services"
        echo "  build    - Rebuild and start services"
        echo "  logs     - Show logs (optionally for specific service)"
        echo "  search   - Run quick search"
        echo "  test     - Test all services"
        echo "  status   - Show service status and stats"
        echo "  results  - Show recent search results"
        echo "  clean    - Clean old result files"
        echo ""
        echo "Examples:"
        echo "  $0 start                    # Start all services"
        echo "  $0 logs scraper-service     # Show scraper logs"
        echo "  $0 search                   # Run quick search"
        ;;
esac
