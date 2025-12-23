
import logging
from datetime import datetime
import os

# Log klasörü oluştur
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Logger yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_info(message):
    """Bilgi logu"""
    logger.info(message)

def log_error(message):
    """Hata logu"""
    logger.error(message)

def log_warning(message):
    """Uyarı logu"""
    logger.warning(message)

def log_success(message):
    """Başarı logu (INFO seviyesinde)"""
    logger.info(f"✓ {message}")

def log_operation(operation, details=""):
    """İşlem logu"""
    message = f"{operation}"
    if details:
        message += f" - {details}"
    logger.info(message)

