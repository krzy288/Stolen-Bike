# Stolen Bike Finder - Kubernetes Manifests

This directory contains Kubernetes manifests for deploying the Stolen Bike Finder application to your EC2 K8s cluster.

## 📁 Files Overview

- **`namespace.yaml`** - Creates the `stolen-bike` namespace
- **`configmap.yaml`** - Application configuration
- **`storage-pvc.yaml`** - Persistent Volume Claim for data storage
- **`storage-service.yaml`** - Storage service deployment and service
- **`scraper-service.yaml`** - Scraper service deployment and service
- **`deploy.sh`** - Linux/Mac deployment script
- **`deploy.bat`** - Windows deployment script

## 🚀 Quick Deployment

### Prerequisites
- `kubectl` installed and configured
- Access to your K8s cluster
- Public ECR images available

### Deploy Everything
```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
deploy.bat
```

### Manual Deployment
```bash
# Create namespace
kubectl apply -f namespace.yaml

# Apply configurations and storage
kubectl apply -f configmap.yaml
kubectl apply -f storage-pvc.yaml

# Deploy services
kubectl apply -f storage-service.yaml
kubectl apply -f scraper-service.yaml
```

## 🔧 Configuration

### Image Tags
The manifests use `:latest` tags. Update them in the YAML files if you want specific versions:
```yaml
image: public.ecr.aws/u7w7e7d5/stolen-bike-storage:v1.0.0
```

### Storage Class
Update the storage class in `storage-pvc.yaml` if needed:
```yaml
storageClassName: gp2  # or your cluster's storage class
```

## 📊 Monitoring

### Check Status
```bash
# Pods
kubectl get pods -n stolen-bike

# Services
kubectl get services -n stolen-bike
```

### View Logs
```bash
# Scraper service logs
kubectl logs -f deployment/scraper-service -n stolen-bike

# Storage service logs
kubectl logs -f deployment/storage-service -n stolen-bike
```

### Port Forwarding (for testing)
```bash
# Access scraper service locally
kubectl port-forward service/scraper-service 8001:8000 -n stolen-bike

# Access storage service locally
kubectl port-forward service/storage-service 8002:8000 -n stolen-bike
```

## 🧹 Cleanup

```bash
# Delete everything
kubectl delete namespace stolen-bike

# Or delete individual components
kubectl delete -f . -n stolen-bike
```

## 🔒 Security Notes

- Services are configured with resource limits
- Health checks are enabled
- Services communicate internally via ClusterIP
- Consider setting up NetworkPolicies for additional security

## 🔧 Accessing the Application

The services run internally within the cluster. For debugging or external access:

### **Port Forwarding (for testing)**
```bash
# Access scraper service locally
kubectl port-forward service/scraper-service 8001:8000 -n stolen-bike

# Access storage service locally  
kubectl port-forward service/storage-service 8002:8000 -n stolen-bike
```

### **If You Need External Access Later**
You can expose services externally by changing the service type:

```yaml
# In storage-service.yaml or scraper-service.yaml
spec:
  type: LoadBalancer  # or NodePort
  ports:
  - port: 8000
    targetPort: 8000
```

## 📈 Scaling

Scale deployments as needed:
```bash
# Scale storage service
kubectl scale deployment storage-service --replicas=3 -n stolen-bike

# Scale scraper service
kubectl scale deployment scraper-service --replicas=2 -n stolen-bike
```
