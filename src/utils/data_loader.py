"""
Excel referans dosyalarını yükleyip, projenin diğer bölümlerinde kullanılabilecek
formatlara dönüştüren yardımcı fonksiyonlar
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
from .logger import get_logger

logger = get_logger(__name__)

class ReferenceData:
    """Referans verilerini yükleyen ve yöneten sınıf"""
    
    def __init__(self, base_path: str = "data/reference"):
        """
        Referans verilerini yükler
        
        Args:
            base_path: Referans dosyalarının bulunduğu klasör yolu
        """
        self.base_path = base_path
        self.data = self._load_all_data()
        logger.info(f"Referans verileri yüklendi: {list(self.data.keys())}")
        
    def _load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Tüm referans Excel dosyalarını yükler"""
        data_dict = {}
        
        try:
            # Excel dosyalarının isimleri ve dosya yolları
            files = {
                "havalimani": os.path.join(self.base_path, "havalimani.xlsx"),
                "kargo": os.path.join(self.base_path, "kargo.xlsx"),
                "restoran_siparis": os.path.join(self.base_path, "restoran-siparis.xlsx"),
                "restoran_rezervasyon": os.path.join(self.base_path, "restoran-rezervasyon.xlsx")
            }
            
            # Her dosyayı yükle
            for key, file_path in files.items():
                if os.path.exists(file_path):
                    data_dict[key] = pd.read_excel(file_path)
                    logger.info(f"{os.path.basename(file_path)} yüklendi: {len(data_dict[key])} satır")
                else:
                    logger.warning(f"{file_path} bulunamadı!")
                    
        except Exception as e:
            logger.error(f"Veri yüklenirken hata oluştu: {str(e)}")
            
        return data_dict
    
    def get_data(self, key: str) -> Optional[pd.DataFrame]:
        """
        Belirli bir veri kaynağını DataFrame olarak döndürür
        
        Args:
            key: Veri kaynağı ismi ('havalimani', 'kargo', 'restoran_siparis', 'restoran_rezervasyon')
            
        Returns:
            İstenilen veri kaynağının DataFrame'i veya bulunamazsa None
        """
        if key in self.data:
            return self.data[key]
        logger.warning(f"'{key}' isimli veri kaynağı bulunamadı")
        return None
    
    def search_data(self, key: str, column: str, search_term: str) -> pd.DataFrame:
        """
        Belirli bir veri kaynağında arama yapar
        
        Args:
            key: Veri kaynağı ismi
            column: Aranacak sütun adı
            search_term: Arama terimi
            
        Returns:
            Arama sonuçlarını içeren DataFrame veya boş DataFrame
        """
        df = self.get_data(key)
        if df is None:
            logger.warning(f"'{key}' veri kaynağı bulunamadığı için arama yapılamıyor")
            return pd.DataFrame()
        
        if column not in df.columns:
            logger.warning(f"'{column}' sütunu '{key}' veri kaynağında bulunamadı. Mevcut sütunlar: {df.columns.tolist()}")
            return pd.DataFrame()
        
        logger.debug(f"'{key}' veri kaynağında '{column}' sütununda '{search_term}' terimi aranıyor")
        
        # Önce tam eşleşme dene
        exact_match = df[df[column] == search_term]
        if not exact_match.empty:
            logger.debug(f"Tam eşleşme bulundu: {len(exact_match)} sonuç")
            return exact_match
            
        # Tam eşleşme bulunamazsa case-insensitive arama yap
        result = df[df[column].str.contains(search_term, case=False, na=False)]
        logger.debug(f"Bulunan sonuç sayısı: {len(result)}")
        
        # Eğer hala bulunamazsa, arama terimini parçalara ayırıp deneyelim
        if result.empty and len(search_term) > 3:
            logger.debug(f"Sonuç bulunamadı, arama terimi parçalara ayrılıyor: {search_term}")
            words = search_term.split()
            for word in words:
                if len(word) >= 3:  # Çok kısa kelimeleri atla
                    word_result = df[df[column].str.contains(word, case=False, na=False)]
                    if not word_result.empty:
                        logger.debug(f"'{word}' kelimesi için {len(word_result)} sonuç bulundu")
                        result = pd.concat([result, word_result]).drop_duplicates()
        
        return result
    
    def get_formatted_data(self, key: str, max_rows: int = 5) -> str:
        """
        Veri kaynağının metin formatında formatlanmış halini döndürür
        
        Args:
            key: Veri kaynağı ismi
            max_rows: Maksimum gösterilecek satır sayısı
            
        Returns:
            Formatlanmış veri metni
        """
        df = self.get_data(key)
        if df is None:
            return "Veri bulunamadı"
        
        # Satır sayısını sınırla
        if len(df) > max_rows:
            df = df.head(max_rows)
            footer = f"\n... ve {len(self.get_data(key)) - max_rows} satır daha"
        else:
            footer = ""
        
        # DataFrame'i metin formatına dönüştür
        formatted_text = df.to_string(index=False)
        
        return formatted_text + footer
    
# Örnek kullanım
if __name__ == "__main__":
    reference_data = ReferenceData()
    
    # Tüm kaynakları yazdır
    for key in reference_data.data.keys():
        print(f"\n{'='*50}")
        print(f"Veri Kaynağı: {key}")
        print(f"{'='*50}")
        print(reference_data.get_formatted_data(key))
    
    # Örnek arama
    search_result = reference_data.search_data("havalimani", "havayolu", "THY")
    if not search_result.empty:
        print("\n\nArama Sonuçları (THY uçuşları):")
        print(search_result.to_string(index=False)) 