# Stolen Bike Finder MVP - Windows Batch Management Script

@echo off
echo 🚴 Stolen Bike Finder MVP - Management Script
echo ==============================================

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="build" goto build
if "%1"=="logs" goto logs
if "%1"=="search" goto search
if "%1"=="test" goto test
if "%1"=="status" goto status
if "%1"=="results" goto results
if "%1"=="clean" goto clean
goto usage

:start
echo 🚀 Starting all services...
docker-compose up -d
timeout /t 5 /nobreak > nul
echo ✅ Services started! Checking health...
curl -s http://localhost:8001/health > nul && echo  ✅ Scraper Service || echo ❌ Scraper Service
curl -s http://localhost:8002/health > nul && echo  ✅ Notification Service || echo ❌ Notification Service
curl -s http://localhost:8003/health > nul && echo  ✅ Storage Service || echo ❌ Storage Service
goto end

:stop
echo 🛑 Stopping all services...
docker-compose down
goto end

:restart
echo 🔄 Restarting all services...
docker-compose down
docker-compose up -d
goto end

:build
echo 🏗️ Rebuilding all services...
docker-compose down
docker-compose up --build -d
goto end

:logs
if "%2"=="" (
    echo 📋 Showing logs for all services...
    docker-compose logs -f
) else (
    echo 📋 Showing logs for %2...
    docker-compose logs -f %2
)
goto end

:search
echo 🔍 Starting quick search...
curl -X GET "http://localhost:8001/search/auto"
goto end

:test
echo 🧪 Testing all services...
echo Testing scraper service...
curl -s http://localhost:8001/health
echo.
echo Testing notification service...
curl -s http://localhost:8002/health
echo.
echo Testing storage service...
curl -s http://localhost:8003/health
echo.
echo Testing notification...
curl -X POST http://localhost:8002/test
goto end

:status
echo 📊 Service Status:
echo ==================
echo|set /p="Scraper Service: "
curl -s http://localhost:8001/health > nul && echo ✅ Running || echo ❌ Down
echo|set /p="Notification Service: "
curl -s http://localhost:8002/health > nul && echo ✅ Running || echo ❌ Down
echo|set /p="Storage Service: "
curl -s http://localhost:8003/health > nul && echo ✅ Running || echo ❌ Down
echo.
echo 📈 Storage Stats:
curl -s http://localhost:8003/stats
goto end

:results
echo 📊 Recent Search Results:
curl -s http://localhost:8003/results
goto end

:clean
echo 🧹 Cleaning old results (keeping last 30 days)...
curl -X DELETE "http://localhost:8003/results?keep_days=30"
goto end

:usage
echo Usage: %0 {start^|stop^|restart^|build^|logs [service]^|search^|test^|status^|results^|clean}
echo.
echo Commands:
echo   start    - Start all services
echo   stop     - Stop all services
echo   restart  - Restart all services
echo   build    - Rebuild and start services
echo   logs     - Show logs (optionally for specific service)
echo   search   - Run quick search
echo   test     - Test all services
echo   status   - Show service status and stats
echo   results  - Show recent search results
echo   clean    - Clean old result files
echo.
echo Examples:
echo   %0 start                    # Start all services
echo   %0 logs scraper-service     # Show scraper logs
echo   %0 search                   # Run quick search

:end
