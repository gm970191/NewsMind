"""
NewsMind FastAPI Application
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.news import router as news_router
from app.api.ai import router as ai_router
from app.services.scheduler import news_scheduler

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

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

def _frontend_file(relative_path: str) -> Path | None:
    """返回构建产物中的文件，拒绝跑出目录。"""
    if not relative_path or not FRONTEND_DIST.is_dir():
        return None
    root = FRONTEND_DIST.resolve()
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        return None
    if candidate.is_file():
        return candidate
    return None


def ensure_database() -> None:
    """建表，并在没有新闻源时写入默认 RSS。"""
    from app.core.database import SessionLocal, create_tables
    from app.models.news import NewsSource

    create_tables()
    defaults = [
        {
            "name": "BBC News",
            "url": "http://feeds.bbci.co.uk/news/rss.xml",
            "type": "rss",
            "category": "国际",
        },
        {
            "name": "CNN",
            "url": "http://rss.cnn.com/rss/edition.rss",
            "type": "rss",
            "category": "国际",
        },
        {
            "name": "TechCrunch",
            "url": "http://feeds.feedburner.com/TechCrunch/",
            "type": "rss",
            "category": "科技",
        },
        {
            "name": "Reuters",
            "url": "http://feeds.reuters.com/reuters/topNews",
            "type": "rss",
            "category": "国际",
        },
    ]
    db = SessionLocal()
    try:
        if db.query(NewsSource).count() > 0:
            return
        for item in defaults:
            db.add(NewsSource(**item))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# 启动调度器
@app.on_event("startup")
async def startup_event():
    """应用启动时建表并初始化调度器"""
    try:
        ensure_database()
    except Exception as e:
        print(f"数据库初始化失败: {e}")
    try:
        news_scheduler.start()
        print("新闻调度器已启动")
    except Exception as e:
        print(f"调度器启动失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时停止调度器"""
    try:
        news_scheduler.stop()
        print("✅ 新闻调度器已停止")
    except Exception as e:
        print(f"❌ 调度器停止失败: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
async def root():
    """页面入口。没有前端构建产物时返回 API 说明。"""
    index = _frontend_file("index.html")
    if index:
        return FileResponse(index)
    return {
        "message": "Welcome to NewsMind API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/{full_path:path}")
async def frontend_routes(full_path: str):
    """静态资源和前端路由。接口路径保持 JSON 404。"""
    asset = _frontend_file(full_path)
    if asset:
        return FileResponse(asset)
    index = _frontend_file("index.html")
    if index and not full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
        return FileResponse(index)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    ) 
