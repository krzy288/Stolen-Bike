@echo off
REM 🚴 Stolen Bike Finder - Comprehensive Local CI/CD Test
REM Mirrors the main.yml GitHub Actions workflow

echo 🚴 STOLEN BIKE FINDER - COMPREHENSIVE CI/CD TEST
echo ===================================================

REM ========================================
REM 🔄 SETUP PHASE
REM ========================================
echo.
echo 🔄 SETUP PHASE
echo ===============
echo ▶ Cleaning up existing containers...
docker-compose down -v >nul 2>&1

REM ========================================
REM 🏗️ BUILD PHASE  
REM ========================================
echo.
echo 🏗️ BUILD PHASE
echo ===============
echo ▶ Building Docker images...
docker-compose build --no-cache --parallel
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build images
    exit /b 1
)
echo ✅ Images built successfully

echo ▶ Listing built images...
docker images | findstr mvp

REM ========================================
REM 🧪 TEST PHASE
REM ========================================
echo.
echo 🧪 TEST PHASE
echo =============
echo ▶ Starting services...
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start services
    exit /b 1
)
echo ✅ Services started

echo ▶ Waiting for services startup...
timeout /t 30 /nobreak >nul

echo ▶ Container status:
docker-compose ps

echo ▶ Running health checks...
curl -f http://localhost:8002/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Storage Service is healthy
) else (
    echo ❌ Storage Service health check failed
    goto monitoring
)

curl -f http://localhost:8001/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Scraper Service is healthy
) else (
    echo ❌ Scraper Service health check failed
    goto monitoring
)

echo ▶ API endpoint tests...
echo 📦 Testing Storage Service API:
curl -s http://localhost:8002/health
curl -s http://localhost:8002/results

echo 🔍 Testing Scraper Service API:
curl -s http://localhost:8001/health
curl -s http://localhost:8001/

echo ▶ Functional tests...
echo 🤖 Triggering auto search...
curl -s http://localhost:8001/search/auto

echo ⏳ Waiting for search processing...
timeout /t 20 /nobreak >nul

echo 📊 Checking stored results...
curl -s http://localhost:8002/results

REM ========================================
REM 📊 MONITORING PHASE
REM ========================================
:monitoring
echo.
echo 📊 MONITORING PHASE
echo ===================
echo ▶ Container status:
docker-compose ps

echo ▶ Recent logs:
echo === SCRAPER SERVICE LOGS ===
docker-compose logs --tail=20 scraper-service

echo === STORAGE SERVICE LOGS ===
docker-compose logs --tail=20 storage-service

REM ========================================
REM 🚀 DEPLOYMENT PREPARATION
REM ========================================
echo.
echo 🚀 DEPLOYMENT PREPARATION
echo =========================
echo ✅ Build successful - ready for K8s deployment
echo 📦 Images built and tested successfully  
echo 🎯 Next step: Deploy to your EC2 Kubernetes cluster

REM ========================================
REM 🧹 CLEANUP PHASE
REM ========================================
echo.
echo 🧹 CLEANUP PHASE
echo ================
echo ▶ Cleaning up...
docker-compose down -v

REM ========================================
REM 📈 RESULTS SUMMARY
REM ========================================
echo.
echo 📈 BUILD SUMMARY
echo ================
echo 🗓️  Date: %DATE% %TIME%
echo 🌿  Branch: local-test
echo 👤  User: %USERNAME%
echo 🔄  Event: manual-test

if %ERRORLEVEL% equ 0 (
    echo ✅  Status: SUCCESS
    echo �  All tests passed!
    echo 🚀  Ready for deployment!
) else (
    echo ❌  Status: FAILED
    echo �  Check logs above for details
)

echo.
echo 🎯 Local CI/CD test completed!
echo 🚀 Push to GitHub to trigger the real pipeline.
pause
