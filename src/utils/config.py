"""
Yapılandırma yönetimi modülü
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

from .logger import get_logger

logger = get_logger(__name__)

class Config:
    """
    Uygulama yapılandırma sınıfı
    Çeşitli yapılandırma kaynaklarını (env, dosya, varsayılanlar) yönetir
    """
    
    # Varsayılan yapılandırma değerleri
    DEFAULTS = {
        "OPENAI_MODEL": "gpt-3.5-turbo",
        "MAX_TOKENS": "500",
        "TEMPERATURE": "0.7", 
        "MAX_CONVERSATION_HISTORY": "10",
        "LOG_LEVEL": "INFO",
        "LOG_FILE": "app.log",
        "REFERENCE_DATA_PATH": "data/reference",
        "DEBUG_MODE": "False"
    }
    
    def __init__(self, config_file: str = ".env"):
        """
        Yapılandırma sınıfını başlatır ve yapılandırma kaynaklarını yükler
        
        Args:
            config_file: Yapılandırma dosyası yolu
        """
        # Yapılandırma değerlerini saklamak için sözlük
        self._config: Dict[str, str] = {}
        
        # .env dosyasını yükle
        self._load_env_file(config_file)
        
        # Çevresel değişkenleri yükle
        self._load_env_vars()
        
        # Eksik değerler için varsayılanları kullan
        self._apply_defaults()
        
        logger.debug(f"Yapılandırma yüklendi: {len(self._config)} değer")
    
    def _load_env_file(self, config_file: str) -> None:
        """
        .env dosyasını yükler
        
        Args:
            config_file: Yapılandırma dosyası yolu
        """
        try:
            # Dosya var mı kontrol et
            env_path = Path(config_file)
            if not env_path.exists():
                logger.warning(f"{config_file} dosyası bulunamadı")
                return
                
            # Dosyayı yükle
            result = load_dotenv(dotenv_path=config_file)
            if result:
                logger.debug(f"{config_file} dosyası başarıyla yüklendi")
            else:
                logger.warning(f"{config_file} dosyası yüklenemedi")
        except Exception as e:
            logger.error(f"Yapılandırma dosyası yüklenirken hata: {str(e)}")
    
    def _load_env_vars(self) -> None:
        """Çevresel değişkenleri yükler"""
        for key in os.environ:
            # Sadece uygulama ile ilgili çevresel değişkenleri al
            if (key.startswith("OPENAI_") or 
                key in self.DEFAULTS or
                key.endswith("_PATH") or 
                key.endswith("_KEY")):
                self._config[key] = os.environ[key]
    
    def _apply_defaults(self) -> None:
        """Varsayılan değerleri uygular"""
        for key, value in self.DEFAULTS.items():
            if key not in self._config:
                self._config[key] = value
                logger.debug(f"Varsayılan değer kullanıldı: {key}={value}")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Yapılandırma değerini getirir
        
        Args:
            key: Yapılandırma anahtarı
            default: Varsayılan değer (eğer anahtar yoksa)
            
        Returns:
            Yapılandırma değeri veya varsayılan değer
        """
        value = self._config.get(key, default)
        
        # API key özel kontrolü
        if key == "OPENAI_API_KEY" and value:
            if value in ["your-api-key-here", "our-api-key-here", "BURAYA_GERCEK_API_KEY_YAZIN"]:
                logger.error("🚨 OpenAI API key hâlâ placeholder değer! Lütfen gerçek API key'inizi .env dosyasına yazın.")
                return None
            elif not value.startswith("sk-"):
                logger.warning("⚠️ OpenAI API key formatı şüpheli. 'sk-' ile başlamalı.")
        
        return value
        
    def set(self, key: str, value: str) -> None:
        """
        Yapılandırma değerini ayarlar
        
        Args:
            key: Yapılandırma anahtarı
            value: Yeni değer
        """
        self._config[key] = value
        logger.debug(f"Yapılandırma değeri ayarlandı: {key}")
        
    def has(self, key: str) -> bool:
        """
        Yapılandırmada bir anahtarın varlığını kontrol eder
        
        Args:
            key: Kontrol edilecek anahtar
            
        Returns:
            Anahtar varsa True, yoksa False
        """
        return key in self._config
        
    def dump(self) -> Dict[str, str]:
        """
        Tüm yapılandırma sözlüğünü döndürür (hassas verileri maskeleyerek)
        
        Returns:
            Yapılandırma sözlüğünün kopyası
        """
        # Hassas verileri maskele
        safe_config = {}
        for key, value in self._config.items():
            if "API_KEY" in key or "SECRET" in key or "PASSWORD" in key or "TOKEN" in key:
                if value:
                    # API anahtarının ilk ve son 4 karakterini göster
                    if len(value) > 8:
                        safe_config[key] = f"{value[:4]}...{value[-4:]}"
                    else:
                        safe_config[key] = "****"  # Çok kısa anahtar
                else:
                    safe_config[key] = "<empty>"
            else:
                safe_config[key] = value
                
        return safe_config
        
    def __str__(self) -> str:
        """Yapılandırmanın okunabilir bir gösterimini döndürür"""
        result = "📝 Yapılandırma:\n"
        result += "━" * 40 + "\n"
        
        # Güvenli yapılandırmayı al ve anahtarlara göre sırala
        safe_config = self.dump()
        for key in sorted(safe_config.keys()):
            result += f"▶ {key}: {safe_config[key]}\n"
            
        return result 