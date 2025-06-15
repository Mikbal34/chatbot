"""
ChatGPT API entegrasyonu için sınıf ve fonksiyonlar
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Union, Tuple
import openai
from openai.types.chat import ChatCompletion

from ..utils.logger import get_logger
from ..utils.config import Config
from ..nlp.preprocessor import preprocess_text
from ..utils.data_loader import ReferenceData

logger = get_logger(__name__)

class ChatGPTIntegration:
    """ChatGPT API entegrasyonu için sınıf"""
    
    def __init__(self, config: Config):
        """
        ChatGPT API entegrasyonu için gerekli ayarları yapar
        
        Args:
            config: Uygulama yapılandırması
        """
        self.config = config
        self.client = None
        self.reference_data = None
        self.active_sector = None  # Aktif sektör (havalimani, kargo, restoran_siparis, restoran_rezervasyon)
        self.conversation_history = []
        self.init_client()
        self.init_reference_data()
        logger.info("ChatGPT entegrasyonu başlatıldı")
        
    def init_client(self) -> None:
        """OpenAI API istemcisini başlatır"""
        try:
            api_key = self.config.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("OpenAI API anahtarı bulunamadı")
                raise ValueError("OpenAI API anahtarı gerekli")
                
            self.client = openai.OpenAI(api_key=api_key)
            logger.debug("OpenAI istemcisi başlatıldı")
        except Exception as e:
            logger.error(f"OpenAI istemcisi başlatılamadı: {str(e)}")
            raise
    
    def init_reference_data(self) -> None:
        """Referans verilerini yükler"""
        try:
            reference_data_path = self.config.get("REFERENCE_DATA_PATH", "data/reference")
            self.reference_data = ReferenceData(base_path=reference_data_path)
            logger.debug("Referans verileri yüklendi")
        except Exception as e:
            logger.warning(f"Referans verileri yüklenemedi: {str(e)}")
            self.reference_data = None
            
    def get_reference_data(self, key: str, search_column: Optional[str] = None, 
                          search_term: Optional[str] = None) -> str:
        """
        Referans verileri içinde arama yapar ve sonucu metin olarak döndürür
        
        Args:
            key: Veri kaynağı anahtarı (havalimani, kargo, restoran_siparis, restoran_rezervasyon)
            search_column: Arama yapılacak sütun (opsiyonel)
            search_term: Aranacak terim (opsiyonel)
            
        Returns:
            Formatlanmış veri veya arama sonuçları metni
        """
        if self.reference_data is None:
            logger.warning("Referans verileri yüklenmemiş")
            return "Referans verileri bulunamadı"
        
        # Eğer arama parametreleri verilmişse, arama yap
        if search_column and search_term:
            results = self.reference_data.search_data(key, search_column, search_term)
            if results.empty:
                return f"'{search_term}' araması için sonuç bulunamadı"
            return results.to_string(index=False)
        
        # Arama parametreleri yoksa tüm veriyi formatlanmış olarak getir
        return self.reference_data.get_formatted_data(key)
            
    def send_message(self, user_message: str, system_prompt: str) -> Dict[str, Any]:
        """
        Kullanıcı mesajını ChatGPT'ye gönderir ve yanıt alır
        
        Args:
            user_message: Kullanıcı mesajı
            system_prompt: ChatGPT için sistem prompt'u
            
        Returns:
            ChatGPT yanıtı
        """
        if not self.client:
            logger.error("OpenAI istemcisi başlatılmamış")
            return {"status": "error", "message": "ChatGPT bağlantısı kurulamadı"}
        
        try:
            # Kullanıcı mesajını önişle
            processed_message = preprocess_text(user_message)
            
            # Referans verileri varsa ve yararlı olabilecekse, sistem promptuna ekle
            context_data = self._get_relevant_context(processed_message)
            if context_data:
                enhanced_system_prompt = f"{system_prompt}\n\nReferans Verileri:\n{context_data}"
            else:
                enhanced_system_prompt = system_prompt
            
            # Mesaj geçmişini ve yeni mesajları hazırla
            messages = [
                {"role": "system", "content": enhanced_system_prompt}
            ]
            
            # Önceki konuşma geçmişini ekle
            for message in self.conversation_history:
                messages.append(message)
                
            # Kullanıcının yeni mesajını ekle
            messages.append({"role": "user", "content": processed_message})
            
            # API isteği gönder
            logger.debug(f"ChatGPT API isteği gönderiliyor: {len(messages)} mesaj")
            response = self.client.chat.completions.create(
                model=self.config.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=messages,
                max_tokens=int(self.config.get("MAX_TOKENS", 500)),
                temperature=float(self.config.get("TEMPERATURE", 0.7))
            )
            
            # Yanıtı al
            assistant_message = response.choices[0].message.content
            
            # Konuşma geçmişini güncelle
            self.conversation_history.append({"role": "user", "content": processed_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Konuşma geçmişini belirli bir uzunlukta tut
            max_history = int(self.config.get("MAX_CONVERSATION_HISTORY", 10))
            if len(self.conversation_history) > max_history * 2:  # Her konuşma 2 mesaj (kullanıcı + asistan)
                self.conversation_history = self.conversation_history[-max_history*2:]
            
            logger.debug(f"ChatGPT yanıtı alındı: {len(assistant_message)} karakter")
            return {
                "status": "success", 
                "message": assistant_message,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"ChatGPT isteği sırasında hata: {str(e)}")
            return {"status": "error", "message": f"Hata: {str(e)}"}

    def _is_code_pattern(self, text: str) -> bool:
        """Bir metnin takip/uçuş/sipariş/rezervasyon numarası formatında olup olmadığını kontrol eder"""
        # Metni temizle
        text = text.strip()
        
        # Sadece rakamlardan oluşan bir mesaj mı? (en az 3 rakam)
        if text.isdigit() and len(text) >= 3:
            logger.debug(f"Sadece rakamlardan oluşan mesaj tespit edildi: {text}")
            return True
            
        # Kargo takip numarası formatları:
        # TR12345678, AB1234567, KRG0010023, vb.
        # Ayrıca sadece numara da olabilir: 1234567890
        kargo_pattern = r'^[A-Za-z]{0,3}\d{5,12}$'
        
        # Uçuş numarası formatı: TK1924, PC3456, XQ123, vb.
        ucus_pattern = r'^[A-Za-z]{1,3}\d{1,4}[A-Za-z]?$'
        
        # Sipariş/rezervasyon numarası formatları: 
        # RS12345, RZ5678, SIP123456, REZ987, R123, RES12, vb.
        siparis_pattern = r'^[A-Za-z]{0,3}\d{2,8}$'
        
        # Herhangi bir formatla eşleşiyor mu kontrol et
        if (re.match(kargo_pattern, text) or 
            re.match(ucus_pattern, text) or 
            re.match(siparis_pattern, text)):
            logger.debug(f"Kod/numara formatı tespit edildi: {text}")
            return True
        
        # Numara içeren bir metin mi kontrol et (içinde en az 3 rakam varsa)
        digit_count = sum(c.isdigit() for c in text)
        if digit_count >= 3 and len(text) <= 20:  # Makul uzunlukta ve yeterli rakam içeren
            logger.debug(f"İçinde numara bulunan kısa metin tespit edildi: {text}")
            return True
            
        return False
    
    def _analyze_conversation_context(self) -> Optional[str]:
        """
        Son birkaç mesajı inceleyerek konuşmanın hangi sektörle ilgili olduğunu belirler
        
        Returns:
            Tespit edilen sektör veya None
        """
        if not self.conversation_history:
            return None
            
        # Son 5 kullanıcı mesajını al (daha geniş bir bağlam için)
        user_messages = []
        for message in reversed(self.conversation_history):
            if message["role"] == "user":
                user_messages.append(message["content"].lower())
                if len(user_messages) >= 5:
                    break
        
        # Mesajları tersine çevir (kronolojik sıra)
        user_messages.reverse()
        
        # Tüm mesajları birleştir
        combined_text = " ".join(user_messages)
        
        # Anahtar kelime setleri - daha geniş
        airport_keywords = ["uçuş", "havalimanı", "uçak", "thy", "pegasus", "bilet", "bagaj", 
                         "terminal", "uçuş numarası", "havayolu", "kalkış", "varış", "kapı", "check-in", 
                         "uçuşum", "uçağım", "havaalanı", "pnr", "uçuş kodu"]
                           
        cargo_keywords = ["kargo", "paket", "teslimat", "takip", "gönderi", "takip numarası", 
                       "taşıma", "gönderim", "sipariş takip", "kurye", "kargom", "kargomu", 
                       "kargo takip", "gönderi", "teslimatım"]
                         
        restaurant_keywords = ["restoran", "yemek", "sipariş", "rezervasyon", "masa", "menü", 
                            "kuryem", "teslim", "yiyecek", "sipariş durumu", "rezervasyonum", 
                            "siparişim", "yemeğim", "restoranım", "masam", "yerim"]
        
        # Rezervasyon özel kelimeleri
        reservation_keywords = ["rezervasyon", "masa", "yer ayırtma", "yer ayırma", "rezerve", 
                               "masa ayırtma", "yer", "kişilik", "masam", "rezervasyonum"]
        
        # Sipariş özel kelimeleri
        order_keywords = ["sipariş", "teslimat", "kuryem", "getirme", "teslim", "paket", 
                         "siparişim", "yemeğim", "yemek durumu"]
        
        # Anahtar kelime eşleşmelerine göre ağırlıklı sektör belirleme
        sector_matches = {
            "havalimani": sum(1 for keyword in airport_keywords if keyword in combined_text),
            "kargo": sum(1 for keyword in cargo_keywords if keyword in combined_text),
            "restoran": sum(1 for keyword in restaurant_keywords if keyword in combined_text)
        }
        
        # Özellikle rezervasyon veya sipariş mi?
        reservation_score = sum(1 for keyword in reservation_keywords if keyword in combined_text)
        order_score = sum(1 for keyword in order_keywords if keyword in combined_text)
        
        # Rezervasyon vs sipariş ayrımı
        if sector_matches["restoran"] > 0:
            if reservation_score > order_score:
                return "restoran_rezervasyon"
            elif order_score > reservation_score:
                return "restoran_siparis"
            else:
                return "restoran_genel"  # Her ikisini de ekleyecek özel durum
        
        # En çok eşleşen sektörü bul
        max_sector = max(sector_matches.items(), key=lambda x: x[1])
        
        # Eğer en az bir eşleşme varsa, o sektörü döndür
        if max_sector[1] > 0:
            return max_sector[0]
            
        return None

    def _get_relevant_context(self, user_message: str) -> Optional[str]:
        """
        Kullanıcı mesajıyla ilgili olabilecek referans verilerini bulur
        Geliştirilmiş bağlam algılama ve kod tanıma özellikleriyle
        
        Args:
            user_message: Kullanıcının mesajı
            
        Returns:
            İlgili referans verileri veya None
        """
        if not self.reference_data:
            logger.warning("Referans verileri bulunamadı, context bilgisi eklenmeyecek")
            return None
        
        # Mesajı küçük harfe çevir
        message_lower = user_message.lower()
        logger.debug(f"Kullanıcı mesajı analiz ediliyor: {message_lower}")
        
        # Havalimanı ile ilgili anahtar kelimeler - genişletilmiş
        airport_keywords = ["uçuş", "havalimanı", "uçak", "thy", "pegasus", "bilet", "bagaj", 
                           "terminal", "uçuş numarası", "havayolu", "kalkış", "varış", "kapı", "check-in",
                           "uçuşum", "uçağım", "havaalanı", "pnr", "uçuş kodu"]
                           
        # Kargo ile ilgili anahtar kelimeler - genişletilmiş
        cargo_keywords = ["kargo", "paket", "teslimat", "takip", "gönderi", "takip numarası", 
                         "taşıma", "gönderim", "sipariş takip", "kurye", "kargom", "kargomu",
                         "kargo takip", "gönderi", "teslimatım"]
                         
        # Restoran ile ilgili anahtar kelimeler - genişletilmiş
        restaurant_keywords = ["restoran", "yemek", "sipariş", "rezervasyon", "masa", "menü", 
                             "kuryem", "teslim", "yiyecek", "sipariş durumu", "rezervasyonum", 
                             "siparişim", "yemeğim", "restoranım", "masam", "yerim"]
        
        # Rezervasyon özel kelimeleri
        reservation_keywords = ["rezervasyon", "masa", "yer ayırtma", "yer ayırma", "rezerve", 
                               "masa ayırtma", "yer", "kişilik", "masam", "rezervasyonum"]
        
        # Sipariş özel kelimeleri
        order_keywords = ["sipariş", "teslimat", "kuryem", "getirme", "teslim", "paket", 
                         "siparişim", "yemeğim", "yemek durumu"]
        
        # Önce sektör kelimelerini kontrol et ve aktif sektörü güncelle
        # Rezervasyon vs sipariş önceliğini belirle
        has_reservation = any(keyword in message_lower for keyword in reservation_keywords)
        has_order = any(keyword in message_lower for keyword in order_keywords)
        
        if any(keyword in message_lower for keyword in cargo_keywords):
            logger.debug(f"Kargo anahtar kelimeleri tespit edildi: {[k for k in cargo_keywords if k in message_lower]}")
            self.active_sector = "kargo"  # Aktif sektörü güncelle
        elif any(keyword in message_lower for keyword in airport_keywords):
            logger.debug(f"Havalimanı anahtar kelimeleri tespit edildi: {[k for k in airport_keywords if k in message_lower]}")
            self.active_sector = "havalimani"  # Aktif sektörü güncelle
        elif any(keyword in message_lower for keyword in restaurant_keywords):
            logger.debug(f"Restoran anahtar kelimeleri tespit edildi: {[k for k in restaurant_keywords if k in message_lower]}")
            # Rezervasyon ile ilgili mi?
            if has_reservation and not has_order:
                self.active_sector = "restoran_rezervasyon"  # Aktif sektörü güncelle
                logger.debug("Rezervasyon ile ilgili anahtar kelimeler tespit edildi")
            # Sipariş ile ilgili mi?
            elif has_order and not has_reservation:
                self.active_sector = "restoran_siparis"  # Aktif sektörü güncelle
                logger.debug("Sipariş ile ilgili anahtar kelimeler tespit edildi")
            else:
                self.active_sector = "restoran_genel"  # Aktif sektörü güncelle
                logger.debug("Genel restoran anahtar kelimeleri tespit edildi")
        
        # Sadece kod/numara içeren bir mesaj mı kontrol et
        is_code_only = self._is_code_pattern(user_message.strip())
        
        # Rezervasyon numarası formatına benzeyen kısa kodlar
        is_reservation_like = False
        reservation_patterns = [r'^R\d{1,5}$', r'^RES\d{1,5}$', r'^REZ\d{1,5}$']
        for pattern in reservation_patterns:
            if re.match(pattern, user_message.strip(), re.IGNORECASE):
                is_reservation_like = True
                logger.debug(f"Rezervasyon numarası formatı tespit edildi: {user_message}")
                break
        
        # Eğer rezervasyon numarası gibi görünüyorsa, aktif sektörü rezervasyon olarak belirle
        if is_reservation_like:
            self.active_sector = "restoran_rezervasyon"
            logger.debug("Rezervasyon numarası formatı tespit edildi, aktif sektör: restoran_rezervasyon")
        
        # Eğer sadece numara/kod içeren bir mesajsa ve aktif sektör varsa, ona göre veri ekle
        if is_code_only:
            logger.debug(f"Mesaj sadece kod/numara içeriyor: {user_message}")
            
            # Aktif sektörü al ya da konuşma geçmişine bakarak belirle
            if not self.active_sector:
                conversation_sector = self._analyze_conversation_context()
                if conversation_sector:
                    self.active_sector = conversation_sector
                    logger.debug(f"Konuşma geçmişinden aktif sektör belirlendi: {self.active_sector}")
            
            # Aktif sektöre göre veri ekle
            if self.active_sector:
                if self.active_sector == "havalimani":
                    try:
                        data = self.reference_data.get_formatted_data("havalimani")
                        logger.debug(f"Kod için havalimanı verileri ekleniyor: {user_message}")
                        return f"Havalimanı verileri:\n{data}"
                    except Exception as e:
                        logger.warning(f"Havalimanı verileri alınamadı: {str(e)}")
                
                elif self.active_sector == "kargo":
                    try:
                        data = self.reference_data.get_formatted_data("kargo")
                        logger.debug(f"Kod için kargo verileri ekleniyor: {user_message}")
                        return f"Kargo takip verileri:\n{data}"
                    except Exception as e:
                        logger.warning(f"Kargo verileri alınamadı: {str(e)}")
                
                elif self.active_sector == "restoran_siparis":
                    try:
                        data = self.reference_data.get_formatted_data("restoran_siparis")
                        logger.debug(f"Kod için restoran sipariş verileri ekleniyor: {user_message}")
                        return f"Restoran sipariş verileri:\n{data}"
                    except Exception as e:
                        logger.warning(f"Restoran sipariş verileri alınamadı: {str(e)}")
                
                elif self.active_sector == "restoran_rezervasyon":
                    try:
                        data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                        logger.debug(f"Kod için restoran rezervasyon verileri ekleniyor: {user_message}")
                        return f"Restoran rezervasyon verileri:\n{data}"
                    except Exception as e:
                        logger.warning(f"Restoran rezervasyon verileri alınamadı: {str(e)}")
                
                elif self.active_sector == "restoran_genel":
                    try:
                        order_data = self.reference_data.get_formatted_data("restoran_siparis")
                        reservation_data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                        logger.debug(f"Kod için tüm restoran verileri ekleniyor: {user_message}")
                        return f"Restoran sipariş verileri:\n{order_data}\n\nRestoran rezervasyon verileri:\n{reservation_data}"
                    except Exception as e:
                        logger.warning(f"Restoran verileri alınamadı: {str(e)}")
            
            # Eğer aktif sektör yoksa, tüm verileri ekle
            else:
                logger.debug("Aktif sektör belirlenemedi, tüm veriler ekleniyor")
                all_data = []
                
                try:
                    airport_data = self.reference_data.get_formatted_data("havalimani")
                    all_data.append(("Havalimanı verileri:", airport_data))
                except Exception as e:
                    logger.warning(f"Havalimanı verileri alınamadı: {str(e)}")
                
                try:
                    cargo_data = self.reference_data.get_formatted_data("kargo")
                    all_data.append(("Kargo takip verileri:", cargo_data))
                except Exception as e:
                    logger.warning(f"Kargo verileri alınamadı: {str(e)}")
                
                try:
                    order_data = self.reference_data.get_formatted_data("restoran_siparis")
                    all_data.append(("Restoran sipariş verileri:", order_data))
                except Exception as e:
                    logger.warning(f"Restoran sipariş verileri alınamadı: {str(e)}")
                
                try:
                    reservation_data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                    all_data.append(("Restoran rezervasyon verileri:", reservation_data))
                except Exception as e:
                    logger.warning(f"Restoran rezervasyon verileri alınamadı: {str(e)}")
                
                if all_data:
                    combined_data = "\n\n".join([f"{title}\n{data}" for title, data in all_data])
                    return combined_data
                    
        # İlişkili veriler ve öncelikler
        relevant_data = []
        
        # Havalimanı ile ilgili mi kontrol et
        if any(keyword in message_lower for keyword in airport_keywords):
            try:
                airport_data = self.reference_data.get_formatted_data("havalimani")
                logger.debug(f"Havalimanı verileri bulundu, {len(airport_data.split('\n'))} satır veri")
                relevant_data.append(("Havalimanı verileri:", airport_data))
            except Exception as e:
                logger.warning(f"Havalimanı verileri alınamadı: {str(e)}")
        
        # Kargo ile ilgili mi kontrol et
        if any(keyword in message_lower for keyword in cargo_keywords):
            try:
                cargo_data = self.reference_data.get_formatted_data("kargo")
                logger.debug(f"Kargo verileri bulundu, {len(cargo_data.split('\n'))} satır veri")
                relevant_data.append(("Kargo takip verileri:", cargo_data))
            except Exception as e:
                logger.warning(f"Kargo verileri alınamadı: {str(e)}")
        
        # Restoran ile ilgili mi kontrol et - sipariş mi rezervasyon mu?
        if any(keyword in message_lower for keyword in restaurant_keywords):
            try:
                # Rezervasyon ile ilgili mi?
                if has_reservation and not has_order:
                    logger.debug("Rezervasyon ile ilgili terimler tespit edildi")
                    reservation_data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                    logger.debug(f"Rezervasyon verileri bulundu, {len(reservation_data.split('\n'))} satır veri")
                    relevant_data.append(("Restoran rezervasyon verileri:", reservation_data))
                # Sipariş ile ilgili mi?
                elif has_order and not has_reservation:
                    logger.debug("Sipariş ile ilgili terimler tespit edildi")
                    order_data = self.reference_data.get_formatted_data("restoran_siparis")
                    logger.debug(f"Sipariş verileri bulundu, {len(order_data.split('\n'))} satır veri")
                    relevant_data.append(("Restoran sipariş verileri:", order_data))
                # Genel restoran sorgusu
                else:
                    logger.debug("Genel restoran sorgusu tespit edildi, tüm restoran verileri ekleniyor")
                    # Hem sipariş hem rezervasyon bilgilerini ekle
                    order_data = self.reference_data.get_formatted_data("restoran_siparis")
                    reservation_data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                    relevant_data.append(("Restoran sipariş verileri:", order_data))
                    relevant_data.append(("Restoran rezervasyon verileri:", reservation_data))
            except Exception as e:
                logger.warning(f"Restoran verileri alınamadı: {str(e)}")
        
        # Eğer ilgili veri yoksa ve active_sector varsa, ona göre veri ekle
        if not relevant_data and self.active_sector:
            logger.debug(f"Mesajda anahtar kelime yok, aktif sektör kullanılıyor: {self.active_sector}")
            
            if self.active_sector == "havalimani":
                try:
                    airport_data = self.reference_data.get_formatted_data("havalimani")
                    relevant_data.append(("Havalimanı verileri:", airport_data))
                except Exception as e:
                    logger.warning(f"Havalimanı verileri alınamadı: {str(e)}")
            
            elif self.active_sector == "kargo":
                try:
                    cargo_data = self.reference_data.get_formatted_data("kargo")
                    relevant_data.append(("Kargo takip verileri:", cargo_data))
                except Exception as e:
                    logger.warning(f"Kargo verileri alınamadı: {str(e)}")
            
            elif self.active_sector == "restoran_siparis":
                try:
                    order_data = self.reference_data.get_formatted_data("restoran_siparis")
                    relevant_data.append(("Restoran sipariş verileri:", order_data))
                except Exception as e:
                    logger.warning(f"Restoran sipariş verileri alınamadı: {str(e)}")
            
            elif self.active_sector == "restoran_rezervasyon":
                try:
                    reservation_data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                    relevant_data.append(("Restoran rezervasyon verileri:", reservation_data))
                except Exception as e:
                    logger.warning(f"Restoran rezervasyon verileri alınamadı: {str(e)}")
            
            elif self.active_sector == "restoran_genel":
                try:
                    order_data = self.reference_data.get_formatted_data("restoran_siparis")
                    reservation_data = self.reference_data.get_formatted_data("restoran_rezervasyon")
                    relevant_data.append(("Restoran sipariş verileri:", order_data))
                    relevant_data.append(("Restoran rezervasyon verileri:", reservation_data))
                except Exception as e:
                    logger.warning(f"Restoran verileri alınamadı: {str(e)}")
        
        # Eğer yine ilgili veri yoksa None döndür
        if not relevant_data:
            # Aktif sektörü konuşma geçmişinden belirle
            if not is_code_only:  # Eğer sadece kod/numara içeren bir mesaj değilse
                conversation_sector = self._analyze_conversation_context()
                if conversation_sector:
                    self.active_sector = conversation_sector
                    logger.debug(f"Konuşma geçmişinden aktif sektör belirlendi: {self.active_sector}")
            
            logger.debug("Mesajda bilinen anahtar kelimeler bulunamadı, referans verisi eklenmeyecek")
            return None
            
        # İlgili verileri birleştir
        context = "\n\n".join([f"{title}\n{data}" for title, data in relevant_data])
        logger.debug(f"Toplam {len(relevant_data)} veri seti eklendi, toplam {len(context.split('\n'))} satır")
        return context
        
    def reset_conversation(self) -> None:
        """Konuşma geçmişini ve aktif sektörü sıfırlar"""
        self.conversation_history = []
        self.active_sector = None
        logger.debug("Konuşma geçmişi ve aktif sektör sıfırlandı") 