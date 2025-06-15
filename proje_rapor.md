# Müşteri Hizmetleri ChatBot - Proje Raporu

## 1. Proje Genel Bakış

Müşteri Hizmetleri ChatBot, yapay zeka destekli ve çoklu sektör desteği sunan bir müşteri hizmetleri asistanıdır. Proje, OpenAI GPT API kullanarak havalimanı, kargo ve restoran hizmetleri için özelleştirilmiş yanıtlar üretebilen bir chatbot uygulamasıdır. Uygulama hem komut satırı (CLI) hem de web arayüzü ile kullanılabilmektedir.

## 2. Proje Yapısı

Proje, modüler bir yapıda organize edilmiştir:

```
├── src/                  # Kaynak kodlar
│   ├── api/              # API entegrasyonları
│   ├── cli/              # Komut satırı arayüzü
│   ├── nlp/              # Doğal dil işleme modülleri
│   ├── utils/            # Yardımcı fonksiyonlar
│   ├── main.py           # Ana uygulama
│   └── web_app.py        # Web uygulaması
├── data/                 # Veri dosyaları
│   └── reference/        # Referans Excel dosyaları
├── logs/                 # Log dosyaları
├── web/                  # Web arayüzü
│   ├── static/           # Statik dosyalar (CSS, JS)
│   └── templates/        # HTML şablonları
├── fix_paths.py          # Dosya yollarını düzenleme betiği
├── requirements.txt      # Gerekli paketler
├── run_app.py            # Uygulama başlatma betiği
├── run_web.py            # Web uygulaması başlatma betiği
└── start_app.bat         # Windows için başlatma dosyası
```

## 3. Temel Bileşenler ve İşlevleri

### 3.1. Ana Uygulama (src/main.py)

Bu dosya, uygulamanın ana giriş noktasıdır. Komut satırı argümanlarını işler ve kullanıcının seçimine göre CLI veya web arayüzünü başlatır.

```python
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
```

### 3.2. Web Uygulaması (src/web_app.py)

Flask tabanlı web arayüzünü yöneten dosyadır. Web sunucusunu başlatır, API endpoint'lerini tanımlar ve HTML şablonlarını sunar.

Önemli bileşenler:
- Flask uygulaması yapılandırması
- Web rotaları (/chat, /api/chat vb.)
- API endpoint'leri

```python
@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chatbot API uç noktası"""
    try:
        data = request.json
        user_message = data.get('message', '')
        sector = data.get('sector', 'all')
        
        if not user_message:
            return jsonify({"status": "error", "message": "Mesaj içeriği boş olamaz"}), 400
        
        # Seçilen sektöre göre sistem promptu belirle
        system_prompt = chat_interface._load_system_prompt(sector)
        
        # ChatGPT'ye mesaj gönder
        logger.debug(f"Web arayüzünden gelen mesaj: '{user_message}', sektör: {sector}")
        response = chatgpt.send_message(user_message, system_prompt)
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"API hatası: {str(e)}")
        return jsonify({"status": "error", "message": f"Hata: {str(e)}"}), 500
```

### 3.3. ChatGPT Entegrasyonu (src/api/chatgpt.py)

OpenAI API ile iletişim kuran ve chatbot'un beyin işlevini yerine getiren modüldür. Kullanıcı mesajlarını işler, OpenAI API'ye gönderir ve yanıtları alır.

Önemli fonksiyonlar:
- `send_message()`: Kullanıcı mesajını OpenAI API'ye gönderir ve yanıt alır
- `_get_relevant_context()`: Kullanıcı mesajına uygun referans verilerini bulur
- `reset_conversation()`: Konuşma geçmişini sıfırlar

```python
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
```

### 3.4. Komut Satırı Arayüzü (src/cli/interface.py)

Komut satırı üzerinden kullanıcıyla etkileşim kuran modüldür. Kullanıcı girdilerini alır, ChatGPT entegrasyonuna iletir ve yanıtları gösterir.

Önemli fonksiyonlar:
- `start()`: CLI uygulamasını başlatır
- `_mode_selection()`: Kullanıcının mod seçmesini sağlar
- `_load_system_prompt()`: Seçilen moda göre sistem promptunu yükler

```python
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
```

### 3.5. Metin Önişleme (src/nlp/preprocessor.py)

Kullanıcı girdilerini işleyen ve normalize eden modüldür. Metin temizleme, dil tespiti ve anahtar kelime çıkarma işlevlerini sağlar.

Önemli fonksiyonlar:
- `preprocess_text()`: Metin verisini önişler ve normalize eder
- `sanitize_input()`: Kullanıcı girdisindeki zararlı içerikleri temizler
- `detect_language()`: Metnin dilini tespit eder
- `extract_keywords()`: Metinden anahtar kelimeleri çıkarır

```python
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
```

### 3.6. Veri Yükleme (src/utils/data_loader.py)

Referans verilerini yükleyen ve yöneten modüldür. Excel dosyalarından veri okur ve bu verileri chatbot'un kullanabileceği formata dönüştürür.

Önemli fonksiyonlar:
- `_load_all_data()`: Tüm referans Excel dosyalarını yükler
- `search_data()`: Belirli bir veri kaynağında arama yapar
- `get_formatted_data()`: Veri kaynağının formatlanmış halini döndürür

```python
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
```

### 3.7. Web Arayüzü (web/templates/ ve web/static/)

Web uygulamasının HTML şablonları ve statik dosyalarını (CSS, JS, resimler) içerir. Kullanıcı dostu bir arayüz sağlar.

#### 3.7.1. HTML Şablonları

- `landing.html`: Karşılama sayfası
- `chat.html`: Sohbet arayüzü

#### 3.7.2. JavaScript (web/static/js/chat.js)

Web arayüzünün etkileşimli özelliklerini sağlayan JavaScript kodunu içerir.

```javascript
function sendMessage() {
    const message = userInput.value.trim();
    if (message === '' || isWaitingForResponse) return;

    // Kullanıcı mesajını ekle
    addMessage(message, 'user');
    userInput.value = '';

    // İlk mesaj için hoş geldin efekti
    if (isFirstUserMessage) {
        isFirstUserMessage = false;
        addWelcomeEffect();
    }

    // Chatbot yanıtı için bekleme durumunu başlat
    isWaitingForResponse = true;
    addTypingIndicator();

    // API isteği gönder
    fetchBotResponse(message, activeSector);

    // Input'a tekrar odaklan
    setTimeout(() => {
        userInput.focus();
    }, 100);
}
```

## 4. Başlatma ve Çalıştırma Dosyaları

### 4.1. run_app.py

Ana uygulamayı başlatan betiktir. Dosya yollarını düzeltir ve web uygulamasını başlatır.

```python
def main():
    # Proje kök dizinini belirle
    project_root = os.path.abspath(os.path.dirname(__file__))
    os.chdir(project_root)
    
    print("=" * 60)
    print("🤖 Müşteri Hizmetleri ChatBot Başlatılıyor...")
    print("=" * 60)
    
    # Dosya yollarını düzelt
    print("\n[1/2] Dosya yolları düzeltiliyor...")
    run_command("python fix_paths.py")
    
    # Web uygulamasını başlat
    print("\n[2/2] Web uygulaması başlatılıyor...\n")
    print("Web arayüzüne erişmek için tarayıcınızda http://localhost:5000 adresini açın")
    print("Uygulamayı durdurmak için CTRL+C tuşlarına basın\n")
    print("=" * 60 + "\n")
    
    # Web uygulamasını başlat
    run_command("python run_web.py")
```

### 4.2. start_app.bat

Windows kullanıcıları için kolay başlatma sağlayan batch dosyasıdır.

```batch
@echo off
echo Musteri Hizmetleri ChatBot baslatiliyor...
python run_app.py
pause 
```

## 5. Veri Kaynakları

Proje, aşağıdaki referans veri kaynaklarını kullanır:

- `data/reference/havalimani.xlsx`: Uçuş ve havalimanı bilgileri
- `data/reference/kargo.xlsx`: Kargo takip bilgileri
- `data/reference/restoran-siparis.xlsx`: Restoran sipariş bilgileri
- `data/reference/restoran-rezervasyon.xlsx`: Restoran rezervasyon bilgileri

## 6. Çevre Değişkenleri

Proje, `.env` dosyasında aşağıdaki çevre değişkenlerini kullanır:

```
# ChatGPT API Configuration
OPENAI_API_KEY=your-api-key-here

# Application Settings
LOG_LEVEL=INFO
LOG_FILE=data/log.txt

# ChatGPT Model Settings
CHATGPT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7
```

## 7. Gerekli Paketler

Proje aşağıdaki Python paketlerine bağımlıdır (requirements.txt):

```
# ChatGPT API
openai==1.58.1

# Environment variables
python-dotenv==1.0.0

# Logging
colorlog==6.8.0

# Data processing
pandas==2.3.0
openpyxl==3.1.5

# Testing
pytest==7.4.4
pytest-cov==4.1.0
pytest-mock==3.12.0

# Type checking
mypy==1.8.0

# Code formatting
black==24.3.0
flake8==7.0.0

# Web Application
flask==3.0.2
flask-cors==4.0.0 
```

## 8. Özet

Müşteri Hizmetleri ChatBot, OpenAI GPT API kullanarak çoklu sektör desteği sunan, hem CLI hem de web arayüzü ile kullanılabilen bir chatbot uygulamasıdır. Modüler yapısı sayesinde kolayca genişletilebilir ve sürdürülebilirdir. Havalimanı, kargo ve restoran hizmetleri için özelleştirilmiş yanıtlar üretebilir ve referans verilerini kullanarak kullanıcı sorularını yanıtlayabilir. 