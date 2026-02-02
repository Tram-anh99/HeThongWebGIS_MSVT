#!/bin/bash
# ========== Database Setup Script ==========
# Script để tạo database và enable PostGIS
# Author: HeThongWebGIS_MSVT

echo "=================================================="
echo "🚀 WebGIS MSVT - Database Setup"
echo "=================================================="

# Database configuration
DB_NAME="webgis_msvt"
DB_USER="postgres"
DB_SCHEMA="public"

echo ""
echo "📊 Database name: $DB_NAME"
echo "👤 User: $DB_USER"
echo "📁 Schema: $DB_SCHEMA"
echo ""

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL status..."
pg_isready -U $DB_USER > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ PostgreSQL is not running!"
    echo "💡 Please start PostgreSQL first"
    exit 1
fi
echo "✅ PostgreSQL is running"

# Check if database exists
echo ""
echo "🔍 Checking if database exists..."
psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME
if [ $? -eq 0 ]; then
    echo "⚠️  Database '$DB_NAME' already exists!"
    read -p "❓ Do you want to drop and recreate it? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo "🗑️  Dropping database..."
        dropdb -U $DB_USER $DB_NAME
        echo "✅ Database dropped"
    else
        echo "ℹ️  Keeping existing database"
        echo "ℹ️  Enabling PostGIS extension..."
        psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;" > /dev/null 2>&1
        echo "✅ PostGIS enabled"
        exit 0
    fi
fi

# Create database
echo ""
echo "📦 Creating database '$DB_NAME'..."
createdb -U $DB_USER $DB_NAME
if [ $? -eq 0 ]; then
    echo "✅ Database created successfully"
else
    echo "❌ Failed to create database"
    exit 1
fi

# Enable PostGIS extension
echo ""
echo "🗺️  Enabling PostGIS extension..."
psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;"
if [ $? -eq 0 ]; then
    echo "✅ PostGIS extension enabled"
    
    # Check PostGIS version
    VERSION=$(psql -U $DB_USER -d $DB_NAME -t -c "SELECT PostGIS_Version();")
    echo "📍 PostGIS version: $VERSION"
else
    echo "❌ Failed to enable PostGIS"
    echo "💡 You may need superuser privileges"
    exit 1
fi

# Set search path
echo ""
echo "🔧 Configuring schema..."
psql -U $DB_USER -d $DB_NAME -c "ALTER DATABASE $DB_NAME SET search_path TO $DB_SCHEMA, public;" > /dev/null 2>&1
echo "✅ Schema configured"

echo ""
echo "=================================================="
echo "✅ Database setup complete!"
echo "=================================================="
echo ""
echo "📋 Next steps:"
echo "   1. Run database migrations"
echo "   2. Import data from VN34 and Learning-Fast-JS"
echo "   3. Start the backend server"
echo ""
