"""
NewsMind FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.news import router as news_router
from app.api.ai import router as ai_router
from app.services.scheduler import news_scheduler

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(news_router, prefix=settings.api_prefix)
app.include_router(ai_router, prefix=settings.api_prefix)

# 启动调度器
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化调度器"""
    try:
        news_scheduler.start()
        print("✅ 新闻调度器已启动")
    except Exception as e:
        print(f"❌ 调度器启动失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时停止调度器"""
    try:
        news_scheduler.stop()
        print("✅ 新闻调度器已停止")
    except Exception as e:
        print(f"❌ 调度器停止失败: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NewsMind API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    ) 