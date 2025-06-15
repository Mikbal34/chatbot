"""
Müşteri Hizmetleri Chatbot CLI Arayüzü
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional, List

from ..utils.config import Config
from ..utils.logger import get_logger
from ..api.chatgpt import ChatGPTIntegration

logger = get_logger(__name__)

class ChatInterface:
    """
    Chatbot için komut satırı arayüzü
    """
    
    def __init__(self, config: Config):
        """
        Arayüzü başlatır
        
        Args:
            config: Uygulama yapılandırması
        """
        self.config = config
        self.chatgpt = ChatGPTIntegration(config)
        self.active_mode = 'general'  # general, advanced, airport, cargo, restaurant
        logger.debug("ChatInterface başlatıldı")
        
    def start(self):
        """CLI uygulamasını başlatır"""
        try:
            self._print_header()
            self._mode_selection()
            
            while True:
                try:
                    # Kullanıcı girdisini al
                    user_input = input("\n🧑‍💼 > ").strip()
                    
                    # Çıkış komutunu kontrol et
                    if user_input.lower() in ['q', 'quit', 'exit', 'çıkış']:
                        print("\n👋 Görüşmek üzere! İyi günler!")
                        break
                        
                    # Sıfırlama komutunu kontrol et
                    if user_input.lower() in ['reset', 'sıfırla', 'yeni']:
                        self.chatgpt.reset_conversation()
                        print("\n🔄 Sohbet sıfırlandı. Yeni bir konuşma başlatıldı.")
                        continue
                        
                    # Mod değiştirme komutunu kontrol et
                    if user_input.lower() in ['mode', 'mod', 'değiştir']:
                        self._mode_selection()
                        continue
                    
                    # Boş girdiyi kontrol et
                    if not user_input:
                        continue
                    
                    # Sistem promptunu yükle
                    system_prompt = self._load_system_prompt(self.active_mode)
                    
                    # Mesajı gönder ve yanıt al
                    logger.debug(f"Kullanıcı mesajı: {user_input}")
                    response = self.chatgpt.send_message(user_input, system_prompt)
                    
                    if response["status"] == "success":
                        print(f"\n🤖 > {response['message']}")
                        
                        # Token kullanımını göster (debug modunda)
                        if self.config.get("DEBUG_MODE") == "True" and "usage" in response:
                            usage = response["usage"]
                            print(f"\n[Debug] Token kullanımı: {usage['prompt_tokens']} (prompt) + "
                                 f"{usage['completion_tokens']} (yanıt) = {usage['total_tokens']} (toplam)")
                    else:
                        print(f"\n⚠️ Hata: {response['message']}")
                
                except KeyboardInterrupt:
                    print("\n\n⚠️ İşlem iptal edildi. Çıkmak için 'q', devam etmek için herhangi bir metin girin.")
                    continue
                    
                except Exception as e:
                    logger.error(f"Mesaj işlenirken hata: {str(e)}", exc_info=True)
                    print(f"\n⚠️ Bir hata oluştu: {str(e)}")
                    print("Lütfen tekrar deneyin veya farklı bir soru sorun.")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Program kapatılıyor... İyi günler!")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Arayüz çalıştırılırken hata: {str(e)}", exc_info=True)
            print(f"\n⛔ Kritik hata: {str(e)}")
            sys.exit(1)
            
    def _print_header(self):
        """Uygulama başlığını ve bilgilerini yazdırır"""
        print("\n" + "=" * 50)
        print("📱 Müşteri Hizmetleri ChatBot")
        print("=" * 50)
        print("✨ Hoş geldiniz! Size nasıl yardımcı olabilirim?")
        print("🔹 Çıkış için 'q' yazabilirsiniz")
        print("🔹 Yeni bir konuşma başlatmak için 'reset' yazabilirsiniz")
        print("🔹 Modu değiştirmek için 'mode' yazabilirsiniz")
        print("=" * 50 + "\n")
        
    def _mode_selection(self):
        """Mod seçim menüsünü gösterir ve seçimi alır"""
        print("\nLütfen bir mod seçin:")
        print("1. Genel Mod (Tüm servisler)")
        print("2. Gelişmiş Mod (Detaylı senaryolar)")
        print("3. Havalimanı Modu")
        print("4. Kargo Modu")
        print("5. Restoran Modu")
        
        while True:
            try:
                choice = input("\nSeçiminiz (1-5): ").strip()
                
                if choice == '1':
                    self.active_mode = 'general'
                    print("\n✅ Genel mod seçildi.")
                    break
                elif choice == '2':
                    self.active_mode = 'advanced'
                    print("\n✅ Gelişmiş mod seçildi.")
                    break
                elif choice == '3':
                    self.active_mode = 'havalimani'
                    print("\n✅ Havalimanı modu seçildi.")
                    break
                elif choice == '4':
                    self.active_mode = 'kargo'
                    print("\n✅ Kargo modu seçildi.")
                    break
                elif choice == '5':
                    self.active_mode = 'restoran'
                    print("\n✅ Restoran modu seçildi.")
                    break
                else:
                    print("⚠️ Geçersiz seçim. Lütfen 1 ile 5 arasında bir sayı girin.")
            
            except KeyboardInterrupt:
                self.active_mode = 'general'
                print("\n\n⚠️ Mod seçimi iptal edildi. Genel mod kullanılacak.")
                break
                
            except Exception as e:
                logger.error(f"Mod seçiminde hata: {str(e)}")
                print(f"\n⚠️ Bir hata oluştu: {str(e)}. Genel mod kullanılacak.")
                self.active_mode = 'general'
                break
                
        logger.debug(f"Seçilen mod: {self.active_mode}")
        
    def _load_system_prompt(self, mode: str) -> str:
        """
        Belirtilen moda göre sistem promptunu yükler
        
        Args:
            mode: Prompt modu (general, advanced, havalimani, kargo, restoran, vb.)
            
        Returns:
            Sistem promptu metni
        """
        # Temel sistem promptu
        base_prompt = """Sen profesyonel bir müşteri hizmetleri asistanısın. 
Sorulara saygılı, yardımsever ve bilgilendirici yanıtlar vermelisin.
Verilen referans bilgileri dahilinde cevap ver. Referans verisinde olmayan bilgileri uydurma.
Yanıtlarını Türkçe olarak ver. Kibar ve profesyonel bir dil kullan."""

        # Genel mod promptu
        if mode in ['general', 'all']:
            return base_prompt + """
Havalimanı, kargo ve restoran hizmetleri hakkında soruları yanıtlayabilirsin.
Kullanıcı bir takip numarası, uçuş kodu veya rezervasyon numarası sorarsa, referans verilerinde ara ve sonucu bildir.
Eğer ilgili bir veri bulamazsan, kullanıcıya durumu nazikçe açıkla ve doğru bilgi için nasıl iletişime geçebileceklerini belirt."""

        # Gelişmiş mod promptu
        elif mode == 'advanced':
            return base_prompt + """
Havalimanı, kargo ve restoran hizmetleri hakkında detaylı bilgi verebilirsin.
Kullanıcı senaryolarına ve özel durumlara uygun, kapsamlı yanıtlar sunmalısın.
Gerektiğinde alternatif çözümler öner ve kullanıcıya ek bilgiler sağla.
Teknik terimler kullanabilir, ancak bunları kullanıcının anlayabileceği şekilde açıklamalısın."""

        # Havalimanı modu promptu
        elif mode == 'havalimani':
            return base_prompt + """
Özellikle havalimanı ve uçuş hizmetleri konusunda uzmanlaşmış bir asistansın.
Uçuş durumları, bagaj takibi, boarding süreçleri ve havalimanı hizmetleri hakkında bilgi verebilirsin.
Uçuş numarası veya PNR kodu sorulduğunda, referans verileri içinde arama yapıp sonuçları göstermelisin.
Havalimanı prosedürleri, güvenlik kontrolleri ve yolcu hakları konusunda da bilgi verebilirsin."""

        # Kargo modu promptu
        elif mode == 'kargo':
            return base_prompt + """
Özellikle kargo ve teslimat hizmetleri konusunda uzmanlaşmış bir asistansın.
Kargo takibi, teslimat süreçleri ve lojistik hizmetler hakkında bilgi verebilirsin.
Takip numarası sorulduğunda, referans verileri içinde arama yapıp sonuçları göstermelisin.
Teslimat gecikmeleri, hasar bildirimleri ve iade süreçleri hakkında da yardımcı olabilirsin."""

        # Restoran modu promptu
        elif mode == 'restoran':
            return base_prompt + """
Özellikle restoran hizmetleri konusunda uzmanlaşmış bir asistansın.
Sipariş takibi, rezervasyon bilgileri ve menü içerikleri hakkında bilgi verebilirsin.
Sipariş numarası veya rezervasyon kodu sorulduğunda, referans verileri içinde arama yapıp sonuçları göstermelisin.
Özel diyet gereksinimleri, ödeme seçenekleri ve restoran kuralları hakkında da bilgi verebilirsin."""

        # Varsayılan prompt
        else:
            logger.warning(f"Bilinmeyen mod: {mode}, genel prompt kullanılıyor")
            return base_prompt + """
Havalimanı, kargo ve restoran hizmetleri hakkında soruları yanıtlayabilirsin.
Kullanıcı bir takip numarası, uçuş kodu veya rezervasyon numarası sorarsa, referans verilerinde ara ve sonucu bildir.
Eğer ilgili bir veri bulamazsan, kullanıcıya durumu nazikçe açıkla ve doğru bilgi için nasıl iletişime geçebileceklerini belirt."""

def parse_arguments():
    """Komut satırı argümanlarını ayrıştırır"""
    parser = argparse.ArgumentParser(description="Müşteri Hizmetleri ChatBot")
    
    parser.add_argument(
        "--config", 
        type=str,
        default=".env",
        help="Yapılandırma dosyası yolu (.env)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log seviyesi"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug modunu etkinleştirir (Detaylı logları gösterir)"
    )
    
    return parser.parse_args()

def main():
    """Ana çalıştırma işlevi"""
    args = parse_arguments()
    
    try:
        # Yapılandırma dosyasını yükle
        config = Config(config_file=args.config)
        
        # Komut satırından log seviyesi belirtildiyse geçersiz kıl
        if args.log_level:
            config.set("LOG_LEVEL", args.log_level)
            
        # CLI arayüzünü başlat
        cli = ChatInterface(config)
        cli.start()
        
    except KeyboardInterrupt:
        print("\n\n👋 Program kapatılıyor... İyi günler!")
        sys.exit(0)
    except Exception as e:
        print(f"\n⛔ Kritik hata: {str(e)}")
        logger.critical(f"Program çalıştırılırken kritik hata: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 