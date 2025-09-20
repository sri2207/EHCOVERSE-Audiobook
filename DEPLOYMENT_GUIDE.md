# EchoVerse Deployment Guide

## 🚀 Local Development Setup

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements_echoverse.txt

# 2. Set up environment
cp .env.template .env
# Edit .env with your IBM Watson credentials

# 3. Launch application
python launch_echoverse.py
```

## 🌐 Production Deployment

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub repository**
   ```bash
   git add .
   git commit -m "Add EchoVerse application"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file: `echoverse_app.py`
   - Add secrets in the Streamlit Cloud dashboard:
     ```toml
     IBM_TTS_API_KEY = "your_api_key"
     IBM_TRANSLATOR_API_KEY = "your_api_key"
     IBM_WATSONX_API_KEY = "your_api_key"
     IBM_WATSONX_PROJECT_ID = "your_project_id"
     ```

### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements_echoverse.txt .
   RUN pip install -r requirements_echoverse.txt
   
   COPY . .
   EXPOSE 8501
   
   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
   
   ENTRYPOINT ["streamlit", "run", "echoverse_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and run container**
   ```bash
   docker build -t echoverse .
   docker run -p 8501:8501 --env-file .env echoverse
   ```

### Option 3: Heroku Deployment

1. **Create Procfile**
   ```
   web: streamlit run echoverse_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-echoverse-app
   heroku config:set IBM_TTS_API_KEY=your_api_key
   heroku config:set IBM_TRANSLATOR_API_KEY=your_api_key
   heroku config:set IBM_WATSONX_API_KEY=your_api_key
   heroku config:set IBM_WATSONX_PROJECT_ID=your_project_id
   git push heroku main
   ```

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# IBM Watson credentials (required)
IBM_TTS_API_KEY=your_watson_tts_api_key
IBM_TRANSLATOR_API_KEY=your_watson_translator_api_key
IBM_WATSONX_API_KEY=your_watsonx_api_key
IBM_WATSONX_PROJECT_ID=your_watsonx_project_id

# Optional configuration
ECHOVERSE_DEBUG=false
ECHOVERSE_MAX_TEXT_LENGTH=50000
ECHOVERSE_RATE_LIMIT_REWRITE=5
ECHOVERSE_RATE_LIMIT_TRANSLATE=10
```

### Development vs Production
```bash
# Development
ECHOVERSE_DEBUG=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Production
ECHOVERSE_DEBUG=false
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

## 📊 Monitoring & Maintenance

### Health Checks
The application includes built-in health monitoring:
- API service status indicators in sidebar
- Error logging and graceful degradation
- Rate limiting to prevent API abuse

### Monitoring Script
```python
# monitor_echoverse.py
import requests
import time
import logging

def check_health():
    try:
        response = requests.get('http://localhost:8501/_stcore/health', timeout=10)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    while True:
        if check_health():
            logging.info("✅ EchoVerse is healthy")
        else:
            logging.error("❌ EchoVerse health check failed")
        time.sleep(300)  # Check every 5 minutes
```

### Log Management
```bash
# View application logs
streamlit run echoverse_app.py > echoverse.log 2>&1

# Rotate logs daily
# Add to crontab:
0 0 * * * mv echoverse.log echoverse.log.$(date +\%Y\%m\%d)
```

## 🔒 Security Considerations

### API Key Security
- **Never commit API keys** to version control
- Use environment variables or secrets management
- Rotate API keys regularly
- Monitor API usage in IBM Cloud dashboard

### Application Security
- Set `STREAMLIT_SERVER_ENABLE_CORS=false` in production
- Use HTTPS in production deployments
- Implement rate limiting for public deployments
- Regular security updates for dependencies

### Resource Limits
```python
# Add to echoverse_app.py for production
import os
MAX_TEXT_LENGTH = int(os.getenv('ECHOVERSE_MAX_TEXT_LENGTH', 50000))
MAX_REQUESTS_PER_MINUTE = int(os.getenv('ECHOVERSE_RATE_LIMIT', 10))
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer for multiple instances
- Implement session affinity for Streamlit
- Consider Redis for session storage

### Performance Optimization
- Cache frequently used voices
- Implement audio file caching
- Use CDN for static assets
- Monitor memory usage and implement cleanup

### Database Integration (Optional)
For enterprise deployments, consider:
- User authentication and profiles
- Usage analytics and billing
- Audio file storage and management
- Audit logging and compliance

## 🆘 Troubleshooting Deployment

### Common Issues

**Port conflicts:**
```bash
# Change port in launch command
streamlit run echoverse_app.py --server.port 8502
```

**Memory issues:**
```bash
# Increase container memory limits
docker run -m 2g -p 8501:8501 echoverse
```

**API timeouts:**
```bash
# Increase timeout in service configurations
REQUESTS_TIMEOUT=60
```

### Performance Tuning
```toml
# ~/.streamlit/config.toml
[server]
maxUploadSize = 200
maxMessageSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[runner]
magicEnabled = false
installTracer = false
fixMatplotlib = false
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Test all features with sample data
- [ ] Verify IBM Watson API credentials
- [ ] Run security scan on dependencies
- [ ] Test error handling and fallbacks
- [ ] Verify rate limiting works correctly

### Deployment
- [ ] Set up environment variables
- [ ] Configure logging and monitoring
- [ ] Test deployment in staging environment
- [ ] Set up health checks
- [ ] Configure backup and recovery

### Post-deployment
- [ ] Monitor application health
- [ ] Check API usage and costs
- [ ] Set up alerting for errors
- [ ] Monitor user feedback
- [ ] Plan regular updates and maintenance

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy EchoVerse
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements_echoverse.txt
    - name: Run tests
      run: python -m pytest tests/
    - name: Deploy to production
      run: echo "Deploy to your platform"
```

---

For additional support with deployment, consult the main README or reach out with specific deployment questions.