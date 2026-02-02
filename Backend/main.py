"""
========== FastAPI Main Application ==========
Hệ thống WebGIS Quản lý Mã số Vùng Trồng (MSVT)
Author: HeThongWebGIS_MSVT
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import engine, Base

# Import all routes
from routes import auth, farms, history, categories, qr, users

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API cho hệ thống WebGIS quản lý mã số vùng trồng",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========== CORS Middleware ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:5173", "http://0.0.0.0:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ========== Include Routers ==========
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(farms.router, prefix=settings.API_PREFIX)
app.include_router(history.router, prefix=settings.API_PREFIX)
app.include_router(categories.router, prefix=settings.API_PREFIX)
app.include_router(qr.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)


# ========== Root Endpoint ==========
@app.get("/")
async def root():
    """API Root - Health check"""
    return {
        "message": "WebGIS MSVT API",
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX
    }


# ========== Health Check ==========
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


# ========== Startup Event ==========
@app.on_event("startup")
async def startup_event():
    """
    Khởi tạo khi start application
    """
    print("=" * 70)
    print(f"🚀 Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🌐 CORS Origins: {settings.cors_origins_list}")
    print(f"📝 API Docs: http://localhost:8000/docs")
    print("=" * 70)


# ========== Shutdown Event ==========
@app.on_event("shutdown")
async def shutdown_event():
    """
    Dọn dẹp khi shutdown application
    """
    print("\n" + "=" * 70)
    print("🛑 Shutting down WebGIS MSVT API")
    print("=" * 70)


# ========== Exception Handlers ==========
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Resource not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
