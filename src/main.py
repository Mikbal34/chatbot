#!/usr/bin/env python3
"""
Müşteri Hizmetleri Chatbot Ana Uygulama
"""

import argparse
import sys
import os

# Proje kök dizinini PATH'e ekle
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.cli.interface import ChatInterface
from src.utils.config import Config
from src.utils.logger import get_logger
from src.web_app import start_web_app

logger = get_logger(__name__)

def main():
    """Ana fonksiyon"""
    # Komut satırı argümanlarını parse et
    parser = argparse.ArgumentParser(description="Müşteri Hizmetleri Chatbot")
    parser.add_argument("--mode", type=str, default="cli", choices=["cli", "web"],
                        help="Çalışma modu: cli (Komut Satırı) veya web (Web Arayüzü)")
    parser.add_argument("--debug", action="store_true",
                        help="Debug modunda çalıştır")
    parser.add_argument("--port", type=int, default=5000,
                        help="Web sunucusu portu (sadece web modu için)")
    
    args = parser.parse_args()
    
    # Config nesnesi oluştur
    config = Config()
    
    # Debug modu etkinleştir (CLI argümanı verilmişse)
    if args.debug:
        config.set("DEBUG_MODE", "True")
        logger.debug("Debug modu aktif")
    
    # Web modunda çalıştır
    if args.mode == "web":
        logger.info("Web modu başlatılıyor...")
        start_web_app(debug=args.debug, port=args.port)
        return
    
    # CLI modunda çalıştır
    logger.info("CLI modu başlatılıyor...")
    chat_interface = ChatInterface(config)
    chat_interface.start()

if __name__ == "__main__":
    main() 