# 🌐 NetOptimizer Pro

**Advanced Network Analysis and Optimization Dashboard**

[![Deploy to Cloud Run](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

## ✨ Features

- 🔍 **Network Analysis** - Full network scan with IP detection, latency measurement, speed test
- 🌐 **DNS Benchmark** - Test 12+ DNS providers including Cloudflare, Google, Quad9, AdGuard
- ☁️ **CDN Testing** - Benchmark 12 CDN providers for optimal content delivery
- 🌍 **Global Ping** - Test latency to 18+ global cloud regions (AWS, GCP, Azure)
- 🔒 **Protocol Testing** - HTTP, HTTPS, TLS 1.2/1.3 benchmark
- 🚪 **Port Scanner** - Scan common and VPN ports
- 💡 **Smart Recommendations** - AI-powered network optimization suggestions
- 📊 **Reports** - Export to JSON/CSV

## 🚀 Deploy to Google Cloud Run

### Option 1: One-Click Deploy

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

### Option 2: Manual Deploy

```bash
# Clone the repository
git clone https://github.com/haniyekshm2003-stack/netoptimizer-pro.git
cd netoptimizer-pro

# Deploy to Cloud Run
gcloud run deploy netoptimizer-pro \
  --source . \
  --region us-central1 \
  --project hallowed-index-476414-n2 \
  --allow-unauthenticated
```

### Option 3: Cloud Build

```bash
gcloud builds submit --config cloudbuild.yaml
```

## 🖥️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Open browser to http://localhost:8080
```

## 📁 Project Structure

```
netoptimizer-pro/
├── main.py                 # FastAPI application
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── cloudbuild.yaml       # Cloud Build config
├── modules/
│   ├── network_scanner.py
│   ├── dns_analyzer.py
│   ├── cdn_tester.py
│   ├── protocol_benchmark.py
│   ├── port_scanner.py
│   ├── global_ping.py
│   ├── recommendation_engine.py
│   └── service_architect.py
└── frontend/
    ├── index.html
    ├── css/style.css
    └── js/app.js
```

## 🌐 Domain Mapping

To map a custom domain (e.g., cloud.tiki2k.com):

1. Go to Cloud Run Console
2. Select your service
3. Click 'Manage Custom Domains'
4. Add your domain
5. Configure DNS as instructed

## 📄 License

MIT License

---

**Built with ❤️ using FastAPI + Python**
