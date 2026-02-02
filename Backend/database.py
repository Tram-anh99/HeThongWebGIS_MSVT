"""
========== Database Connection Module ==========
Quản lý kết nối đến PostgreSQL database với PostGIS support
Author: HeThongWebGIS_MSVT
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== SQLAlchemy Setup ==========

# Tạo database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set True để log tất cả SQL queries
    pool_pre_ping=True,  # Test connection trước khi sử dụng
    pool_size=10,  # Số connection trong pool
    max_overflow=20  # Số connection thêm khi pool đầy
)

# Tạo session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class cho tất cả models
Base = declarative_base()


# ========== Database Helper Functions ==========

def get_db():
    """
    Dependency function để lấy database session
    
    Usage trong FastAPI:
        @app.get("/api/endpoint")
        def some_endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test kết nối đến database
    
    Returns:
        bool: True nếu kết nối thành công, False nếu thất bại
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("✅ Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def check_postgis() -> bool:
    """
    Kiểm tra PostGIS extension đã được cài đặt chưa
    
    Returns:
        bool: True nếu PostGIS đã cài, False nếu chưa
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT PostGIS_Version();"))
            version = result.fetchone()[0]
            logger.info(f"✅ PostGIS version: {version}")
            return True
    except Exception as e:
        logger.warning(f"⚠️  PostGIS not found: {e}")
        logger.info("💡 To install PostGIS, run: CREATE EXTENSION postgis;")
        return False


def init_postgis():
    """
    Khởi tạo PostGIS extension nếu chưa có
    Cần quyền superuser
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            connection.commit()
            logger.info("✅ PostGIS extension initialized!")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize PostGIS: {e}")
        logger.info("💡 You may need superuser privileges. Run manually:")
        logger.info("    psql -U postgres -d webgis_msvt -c 'CREATE EXTENSION postgis;'")
        return False


def get_table_count() -> dict:
    """
    Đếm số lượng tables trong schema hiện tại
    
    Returns:
        dict: {
            'schema': 'public',
            'count': 15
        }
    """
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = :schema
                AND table_type = 'BASE TABLE'
            """)
            result = connection.execute(query, {"schema": settings.DB_SCHEMA})
            count = result.fetchone()[0]
            return {
                "schema": settings.DB_SCHEMA,
                "count": count
            }
    except Exception as e:
        logger.error(f"Error getting table count: {e}")
        return {
            "schema": settings.DB_SCHEMA,
            "count": 0
        }


def create_all_tables():
    """
    Tạo tất cả tables từ models
    Gọi sau khi đã define tất cả models
    """
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ All tables created!")


# ========== Database Initialization ==========

if __name__ == "__main__":
    """Test database connection khi run trực tiếp module này"""
    print("=" * 50)
    print("Testing Database Connection...")
    print("=" * 50)
    
    # Test connection
    if test_connection():
        print("\n✅ Database connection: OK")
    else:
        print("\n❌ Database connection: FAILED")
        exit(1)
    
    # Check PostGIS
    print("\nChecking PostGIS extension...")
    if not check_postgis():
        print("\n⚠️  PostGIS not installed!")
        print("Attempting to install PostGIS...")
        init_postgis()
    
    # Get table info
    table_info = get_table_count()
    print(f"\n📊 Schema: {table_info['schema']}")
    print(f"📊 Total tables: {table_info['count']}")
    
    print("\n" + "=" * 50)
    print("Database check complete!")
    print("=" * 50)
