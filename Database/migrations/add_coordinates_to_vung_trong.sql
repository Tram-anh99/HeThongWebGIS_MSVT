-- Migration: Add latitude and longitude columns to vung_trong table
-- Date: 2026-02-02
-- Description: Add GPS coordinates support for farms

-- Add latitude column
ALTER TABLE vung_trong 
ADD COLUMN IF NOT EXISTS latitude NUMERIC(10, 7) NULL;

-- Add longitude column
ALTER TABLE vung_trong 
ADD COLUMN IF NOT EXISTS longitude NUMERIC(10, 7) NULL;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_vung_trong_coordinates 
ON vung_trong (latitude, longitude);

-- Add comment to columns
COMMENT ON COLUMN vung_trong.latitude IS 'Vĩ độ GPS của vùng trồng';
COMMENT ON COLUMN vung_trong.longitude IS 'Kinh độ GPS của vùng trồng';
