"""
Metin işleme ve önişleme modülü
"""

import re
import unicodedata
import logging
from typing import Tuple, Optional, List

from ..utils.logger import get_logger

logger = get_logger(__name__)

def preprocess_text(text: str) -> str:
    """
    Metin verisini önişler ve normalize eder
    
    Args:
        text: İşlenecek metin
        
    Returns:
        İşlenmiş metin
    """
    if not text:
        return ""
        
    try:
        # Unicode normalize
        text = unicodedata.normalize('NFC', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Emoji desteği - emojileri koru
        
        # Özel karakterleri koru - özel çözümlemeler burada
        
        logger.debug(f"Metin önişleme yapıldı: {len(text)} karakter")
        return text
        
    except Exception as e:
        logger.error(f"Metin önişleme hatası: {str(e)}")
        return text

def sanitize_input(text: str) -> Tuple[str, bool]:
    """
    Kullanıcı girdisindeki zararlı veya uygunsuz içerikleri temizler
    
    Args:
        text: Kullanıcı girdisi
        
    Returns:
        (temizlenmiş_metin, geçerli_mi) ikilisi
    """
    if not text or not text.strip():
        return "Boş mesaj gönderemezsiniz.", False
        
    # Maksimum karakter sayısı
    if len(text) > 1000:
        return f"Mesajınız çok uzun ({len(text)} karakter). Lütfen 1000 karakterden kısa bir mesaj yazın.", False
        
    # Potansiyel zararlı karakterleri temizle
    # Bu fonksiyon geliştirilebilir, şimdilik temel koruma
    
    return preprocess_text(text), True
    
def detect_language(text: str) -> str:
    """
    Metnin dilini tespit eder (basit tespit)
    
    Args:
        text: İncelenecek metin
        
    Returns:
        'tr', 'en' veya 'other'
    """
    # Türkçe'ye özgü karakterler
    tr_letters = 'çğıöşüÇĞİÖŞÜ'
    tr_count = sum(c in tr_letters for c in text)
    
    # Basit bir oran hesabı
    if tr_count > 0 and tr_count / len(text) > 0.05:
        return 'tr'
    
    # İngilizce tespiti daha karmaşık olabilir
    # Şimdilik varsayılan olarak İngilizce kabul ediyoruz
    return 'en'

def extract_keywords(text: str) -> List[str]:
    """
    Metinden temel anahtar kelimeleri çıkarır
    
    Args:
        text: İşlenecek metin
    
    Returns:
        Anahtar kelimeler listesi
    """
    # Türkçe stop wordler
    stop_words = {
        've', 'veya', 'ama', 'fakat', 'ancak', 'için', 'ile', 
        'bir', 'bu', 'şu', 'o', 'ben', 'sen', 'biz', 'siz',
        'onlar', 'da', 'de', 'ki', 'mi', 'mu', 'mı', 'ne', 'ya'
    }
    
    # Metni küçük harfe çevir ve kelimelerine ayır
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Stop wordleri ve çok kısa kelimeleri filtreleme
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Tekrar eden kelimeleri kaldır ve sıklığa göre sırala
    unique_keywords = sorted(set(keywords), key=keywords.count, reverse=True)
    
    # En önemli anahtar kelimeleri döndür (maksimum 10)
    return unique_keywords[:10] 