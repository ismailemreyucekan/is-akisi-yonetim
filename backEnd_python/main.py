from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import workflows, issues
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="İş Akışı Yönetimi API",
    description="Workflow ve Issue yönetimi için REST API",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik origin'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(workflows.router)
app.include_router(issues.router)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "API çalışıyor"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "İş Akışı Yönetimi API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "workflows": "/api/workflows",
            "issues": "/api/issues",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    print(f"🚀 Server {port} portunda çalışıyor")
    print(f"📡 Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"📡 API: http://localhost:{port}/api")
    print(f"🏥 Health Check: http://localhost:{port}/api/health")
    print(f"📋 Workflows: http://localhost:{port}/api/workflows")
    print(f"🐛 Issues: http://localhost:{port}/api/issues")
    print(f"📚 Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)

