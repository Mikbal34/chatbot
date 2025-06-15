# Müşteri Hizmetleri Chatbot - Kurulum ve Çalıştırma Kılavuzu

Bu doküman, Müşteri Hizmetleri Chatbot projesinin nasıl kurulacağını ve çalıştırılacağını detaylı bir şekilde açıklamaktadır.

## 📋 İçindekiler

- [Gereksinimler](#gereksinimler)
- [Kurulum Adımları](#kurulum-adımları)
- [Proje Yapısı](#proje-yapısı)
- [Ortam Değişkenleri Yapılandırması](#ortam-değişkenleri-yapılandırması)
- [Projeyi Çalıştırma](#projeyi-çalıştırma)
- [Web Arayüzüne Erişim](#web-arayüzüne-erişim)
- [Sorun Giderme](#sorun-giderme)

## 🛠️ Gereksinimler

Projeyi çalıştırmak için aşağıdaki yazılımlara ihtiyacınız vardır:

- **Python 3.8+** - [Python'u indirmek için tıklayın](https://www.python.org/downloads/)
- **Git** (isteğe bağlı) - [Git'i indirmek için tıklayın](https://git-scm.com/downloads)
- **OpenAI API Anahtarı** - [OpenAI websitesinden](https://platform.openai.com/) bir API anahtarı almalısınız

## 💻 Kurulum Adımları

### 1. Projeyi İndirme

Projeyi Git kullanarak klonlayabilir veya GitHub'dan ZIP olarak indirebilirsiniz.

**Git ile klonlama:**

```bash
git clone [proje-git-adresi]
cd bionluk_bot
```

**Zip olarak indirme:**
- Projeyi ZIP dosyası olarak indirin
- Dosyaları bilgisayarınızdaki istediğiniz bir klasöre çıkarın (örneğin: `C:\Projects\bionluk_bot` veya `/home/kullanici/bionluk_bot`)
- Komut isteminde/terminalde çıkarılan dizine gidin

### 2. Python Sanal Ortamı Oluşturma (Önerilen)

Bağımlılık çakışmalarını önlemek için bir sanal ortam oluşturmanız önerilir.

**Windows:**

```bash
cd bionluk_bot
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
cd bionluk_bot
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleme

Projenin kök dizininde (bionluk_bot klasörü içinde) aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
```

Bu komut, projeyi çalıştırmak için gerekli tüm Python paketlerini yükleyecektir.

## 📁 Proje Yapısı

Projenin ana dizinleri ve dosyaları aşağıdaki gibidir:

```
bionluk_bot/
├── src/                    # Kaynak kodları
│   ├── api/                # API entegrasyonları ve ChatGPT bağlantıları
│   ├── cli/                # Komut satırı arayüzü
│   ├── nlp/                # Doğal dil işleme modülleri
│   ├── utils/              # Yardımcı fonksiyonlar
│   ├── web_app.py          # Web uygulaması ana modülü
│   └── main.py             # Ana uygulama başlangıç noktası
├── web/                    # Web arayüzü dosyaları
│   ├── templates/          # HTML şablonları
│   └── static/             # CSS, JS, resimler vb.
├── data/                   # Veri dosyaları
│   ├── reference/          # Referans verileri
│   └── log.txt             # Log dosyası
├── logs/                   # Log dosyaları dizini
├── requirements.txt        # Python bağımlılıkları
├── example.env             # Örnek çevre değişkenleri dosyası
├── .env                    # (Siz oluşturacaksınız) Çevre değişkenleri
├── run_app.py              # Ana uygulama başlatma betiği
├── run_web.py              # Web arayüzü başlatma betiği
├── fix_paths.py            # Dosya yollarını düzenleme betiği
└── start_app.bat           # Windows için başlatma betiği
```

**Önemli Dosya ve Klasörler:**

1. **src/**: Tüm kaynak kodu bu dizinde bulunur
2. **web/**: Web arayüzü dosyaları bu dizinde bulunur
3. **data/**: Veriler ve loglar burada saklanır
4. **run_app.py**: Uygulamayı başlatmak için ana betik
5. **requirements.txt**: Gerekli Python paketlerinin listesi
6. **.env**: API anahtarları ve diğer gizli bilgiler (siz oluşturacaksınız)

## ⚙️ Ortam Değişkenleri Yapılandırması

1. Proje kök dizininde `example.env` dosyasını `.env` olarak kopyalayın:

**Windows:**

```bash
copy example.env .env
```

**macOS/Linux:**

```bash
cp example.env .env
```

2. `.env` dosyasını bir metin editörü ile açın (Notepad, VS Code, vb.) ve aşağıdaki değişkenleri yapılandırın:

```
# ChatGPT API Configuration
OPENAI_API_KEY=your-api-key-here  # OpenAI API anahtarınızı buraya yazın

# Application Settings
LOG_LEVEL=INFO  # Loglama seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FILE=data/log.txt  # Log dosyasının konumu

# ChatGPT Model Settings
CHATGPT_MODEL=gpt-3.5-turbo  # Kullanılacak OpenAI modeli
MAX_TOKENS=1000  # Maksimum token sayısı
TEMPERATURE=0.7  # Yanıtların çeşitliliğini belirleyen değer (0.0-1.0)
```

> ⚠️ **Önemli:** Projenin çalışması için geçerli bir OpenAI API anahtarı gereklidir. API anahtarınızı [OpenAI Dashboard](https://platform.openai.com/api-keys) adresinden alabilirsiniz.

## 🚀 Projeyi Çalıştırma

Projeyi çalıştırmak için iki yöntem bulunmaktadır:

### 1. Batch Dosyası ile Çalıştırma (Windows)

Windows kullanıyorsanız:

1. Dosya gezgininde `bionluk_bot` klasörüne gidin
2. `start_app.bat` dosyasını çift tıklayarak çalıştırın

Bu, bir komut istemi penceresi açacak ve uygulamayı otomatik olarak başlatacaktır.

### 2. Python Betiği ile Çalıştırma (Tüm İşletim Sistemleri)

Komut isteminde/terminalde proje kök dizinindeyken (bionluk_bot klasörü içinde) aşağıdaki komutu çalıştırın:

```bash
# Windows
python run_app.py

# macOS/Linux
python3 run_app.py
```

Bu komut:
1. Gerekli dosya yollarını düzeltecek (`fix_paths.py` betiği ile)
2. Web uygulamasını başlatacak (`run_web.py` betiği ile)

Uygulama başarıyla başlatıldığında konsol ekranında aşağıdaki gibi bir çıktı görmelisiniz:

```
============================================================
🤖 Müşteri Hizmetleri ChatBot Başlatılıyor...
============================================================

[1/2] Dosya yolları düzeltiliyor...
Dosya yolları başarıyla güncellendi!

[2/2] Web uygulaması başlatılıyor...

Web arayüzüne erişmek için tarayıcınızda http://localhost:5000 adresini açın
Uygulamayı durdurmak için CTRL+C tuşlarına basın

============================================================
 * Serving Flask app 'src.web_app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

## 🌐 Web Arayüzüne Erişim

Uygulama başarıyla başlatıldığında, web arayüzüne aşağıdaki URL'den erişebilirsiniz:

```
http://localhost:5000
```

Tarayıcınızda (Chrome, Firefox, Edge vb.) bu adresi açın ve müşteri hizmetleri chatbot'unu kullanmaya başlayın.

**Web Arayüzü Kullanımı:**

1. Ana sayfada sohbet arayüzünü göreceksiniz
2. Metin kutusuna müşteri sorusunu yazın ve "Gönder" butonuna tıklayın
3. ChatBot soruyu işleyecek ve yanıt verecektir
4. Tüm sohbet geçmişi sayfada görüntülenir ve `data/` klasöründe saklanır

## ❓ Sorun Giderme

### Yaygın Hatalar ve Çözümleri

1. **"ModuleNotFoundError: No module named 'xyz'"**
   - Çözüm: Tüm bağımlılıkları yüklediğinizden emin olun: `pip install -r requirements.txt`
   - Sanal ortamı aktif ettiğinizden emin olun (Windows: `venv\Scripts\activate`, macOS/Linux: `source venv/bin/activate`)

2. **"Error: Authentication failed - Invalid API key"**
   - Çözüm: `.env` dosyasında geçerli bir OpenAI API anahtarı belirttiğinizden emin olun
   - API anahtarınızın doğru formatta olduğunu kontrol edin (sk- ile başlamalı)
   - OpenAI hesabınızda kredinin olduğunu kontrol edin

3. **Web uygulaması başlatılamıyor - "Address already in use"**
   - Çözüm: 5000 numaralı port başka bir uygulama tarafından kullanılıyor. `src/web_app.py` dosyasını açın ve port numarasını değiştirin (örneğin 5001 olarak).

4. **"Permission denied" hatası**
   - Çözüm: Komut istemini/terminali yönetici olarak çalıştırmayı deneyin
   - Dosya izinlerini kontrol edin (`data/` ve `logs/` klasörlerinin yazılabilir olduğundan emin olun)

5. **"ImportError: Cannot import name X from Y"**
   - Çözüm: Proje dosyalarını değiştirmediyseniz, Python sürüm uyumsuzluğu olabilir. Python 3.8 veya daha yeni bir sürüm kullandığınızdan emin olun.

### Logları Kontrol Etme

Hata ayıklama için logları kontrol edin:

**Windows:**
```bash
type data\log.txt
```

**macOS/Linux:**
```bash
cat data/log.txt
# veya
tail -f data/log.txt
```

Ya da `logs` dizinindeki diğer log dosyalarını inceleyebilirsiniz.

### Dosya Yolları Sorunları

Dosya yolları ile ilgili sorunlar yaşıyorsanız, `fix_paths.py` betiğini manuel olarak çalıştırın:

```bash
python fix_paths.py
```

Bu betik, proje içindeki tüm dosya yollarını düzeltecektir.

## 📞 Destek

Herhangi bir sorunla karşılaşırsanız veya daha fazla yardıma ihtiyacınız varsa, lütfen aşağıdaki kanallardan iletişime geçin:

- E-posta: [destek-email-adresi]
- GitHub Issues: [proje-issues-adresi]

---

© 2024 Müşteri Hizmetleri Chatbot. Tüm hakları saklıdır. 