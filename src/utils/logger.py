"""
Loglama modülü - Çeşitli loglama işlevleri sağlar
"""

import os
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union

import colorlog

# Log dizini
LOG_DIR = Path("logs")

def configure_logging(log_level: str = "INFO", log_file: str = "app.log") -> None:
    """
    Loglama sistemini yapılandırır
    
    Args:
        log_level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log dosyası yolu
    """
    # Log dizinini oluştur
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Log dosyası yolu
    log_file_path = LOG_DIR / log_file

    # Log formatı
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Renkli konsol formatı
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s%(reset)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        }
    )
    
    # Root logger'ı yapılandır
    root_logger = logging.getLogger()
    
    # Log seviyesi
    level = getattr(logging, log_level.upper())
    root_logger.setLevel(level)
    
    # İki defa yapılandırma olmasın diye mevcut handler'ları temizle
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Dosya handler'ı ekle
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Konsol handler'ı ekle
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Başlangıç log mesajı
    root_logger.info(f"Loglama sistemi başlatıldı (seviye: {log_level})")

def get_logger(name: str) -> logging.Logger:
    """
    Belirli bir modül için logger döndürür
    
    Args:
        name: Logger ismi (genellikle __name__ kullanılır)
        
    Returns:
        İstenilen logger
    """
    return logging.getLogger(name)

def log_data_access(logger: logging.Logger, data_type: str, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Veri erişim olaylarını loglar
    
    Args:
        logger: Kullanılacak logger
        data_type: Veri tipi (örneğin 'havalimani', 'kargo')
        operation: İşlem tipi (örneğin 'read', 'search')
        details: Ek detaylar
    """
    message = f"Veri erişimi: {data_type} - {operation}"
    if details:
        message += f" - Detaylar: {details}"
    logger.info(message)

def log_api_request(logger: logging.Logger, api_name: str, endpoint: str, 
                    request_data: Optional[Dict[str, Any]] = None, 
                    response_status: Optional[Union[str, int]] = None,
                    response_time: Optional[float] = None) -> None:
    """
    API isteklerini loglar
    
    Args:
        logger: Kullanılacak logger
        api_name: API adı (örneğin 'openai')
        endpoint: API endpoint'i
        request_data: İstek verileri
        response_status: Yanıt durumu
        response_time: Yanıt süresi (saniye)
    """
    message = f"API isteği: {api_name} - {endpoint}"
    
    if response_status is not None:
        message += f" - Durum: {response_status}"
    
    if response_time is not None:
        message += f" - Süre: {response_time:.2f}s"
    
    if request_data and logger.level <= logging.DEBUG:
        sensitive_fields = ['api_key', 'token', 'password', 'secret']
        safe_data = {k: ('***' if k.lower() in sensitive_fields else v) for k, v in request_data.items()}
        message += f" - Veri: {safe_data}"
    
    logger.info(message) 