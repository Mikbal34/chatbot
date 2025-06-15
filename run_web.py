#!/usr/bin/env python3
"""
Müşteri Hizmetleri Chatbot Web Uygulaması Başlatma Betiği
"""

import sys
import os

# Proje kök dizinini PATH'e ekle
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.web_app import start_web_app

if __name__ == "__main__":
    # Web uygulamasını başlat
    print("Müşteri Hizmetleri Chatbot Web Uygulaması başlatılıyor...")
    print("Web arayüzüne erişmek için tarayıcınızda http://localhost:5000 adresini açın")
    start_web_app(debug=True, port=5000)