# QR Code Generation Utilities
import qrcode
from io import BytesIO
from typing import Optional


def generate_qr_code(data: str, size: int = 300) -> BytesIO:
    """
    Generate QR code image
    
    Args:
        data: Data to encode in QR code
        size: Size of QR code in pixels
    
    Returns:
        BytesIO: QR code image as bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io


def generate_farm_qr_url(ma_vung: str, base_url: str = "http://localhost:5173") -> str:
    """
    Generate URL for farm traceability
    
    Args:
        ma_vung: Farm code
        base_url: Base URL of frontend application
    
    Returns:
        str: Full URL for QR code (points to frontend trace page)
    """
    return f"{base_url}/trace/{ma_vung}"


def generate_farm_qr_code(ma_vung: str, base_url: str = "http://localhost:5173") -> BytesIO:
    """
    Generate QR code for farm traceability
    
    Args:
        ma_vung: Farm code
        base_url: Base URL of frontend application
    
    Returns:
        BytesIO: QR code image
    """
    url = generate_farm_qr_url(ma_vung, base_url)
    return generate_qr_code(url)
