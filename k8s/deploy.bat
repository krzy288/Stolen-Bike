@echo off
REM Stolen Bike Finder - Kubernetes Deployment Script for Windows
REM This script deploys the application to your K8s cluster

echo 🚴 Deploying Stolen Bike Finder to Kubernetes...

REM Check if kubectl is available
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo ❌ kubectl is not installed or not in PATH
    exit /b 1
)

REM Check if we can connect to the cluster
echo 🔍 Checking cluster connection...
kubectl cluster-info >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot connect to Kubernetes cluster
    echo Please check your kubeconfig and cluster connectivity
    exit /b 1
)

echo ✅ Connected to cluster
kubectl config current-context

REM Create namespace
echo 🌐 Creating namespace...
kubectl apply -f namespace.yaml

REM Apply configurations
echo ⚙️ Applying configurations...
kubectl apply -f configmap.yaml

REM Create storage
echo 💾 Creating persistent storage...
kubectl apply -f storage-pvc.yaml

REM Deploy services
echo 🚀 Deploying services...
kubectl apply -f storage-service.yaml
kubectl apply -f scraper-service.yaml

REM Wait for deployments to be ready
echo ⏳ Waiting for deployments to be ready...
kubectl rollout status deployment/storage-service -n stolen-bike --timeout=300s
kubectl rollout status deployment/scraper-service -n stolen-bike --timeout=300s

REM Show deployment status
echo 📊 Deployment Status:
echo ===================
kubectl get pods -n stolen-bike
echo.
kubectl get services -n stolen-bike

echo.
echo ✅ Deployment completed successfully!
echo 🎉 Stolen Bike Finder is now running in the 'stolen-bike' namespace
echo.
echo 📝 Useful commands:
echo    kubectl get pods -n stolen-bike
echo    kubectl logs -f deployment/scraper-service -n stolen-bike
echo    kubectl logs -f deployment/storage-service -n stolen-bike
echo    kubectl port-forward service/scraper-service 8001:8000 -n stolen-bike
echo    kubectl port-forward service/storage-service 8002:8000 -n stolen-bike

pause
