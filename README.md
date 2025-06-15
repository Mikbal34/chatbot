# Müşteri Hizmetleri ChatBot

Yapay zeka destekli, çoklu sektör desteği sunan müşteri hizmetleri asistanı.

![Screenshot](screenshot.png)

## Özellikler

- **Çoklu Sektör Desteği**: Havalimanı, kargo ve restoran hizmetleri için özelleştirilmiş yanıtlar
- **Metin Analizi**: Kullanıcı mesajlarından bağlam ve sektör bilgisini otomatik tespit eder
- **Takip Kodu Tanıma**: Uçuş, kargo ve rezervasyon takip kodlarını otomatik olarak tanır
- **İki Farklı Arayüz**: Hem komut satırı (CLI) hem de web arayüzü ile kullanım imkanı
- **Mobil Uyumlu**: Responsive tasarım ile her cihazda çalışır
- **Koyu Tema**: Modern ve göz yorgunluğunu azaltan tasarım

## Ekran Görüntüleri

### Web Arayüzü - Karşılama Sayfası

![Landing Page](screenshots/landing.png)

### Web Arayüzü - Chat Sayfası

![Chat Page](screenshots/chat.png)

### Komut Satırı Arayüzü

![CLI Interface](screenshots/cli.png)

## Kurulum

1. Projeyi klonlayın:

```bash
git clone https://github.com/username/musteri-hizmetleri-chatbot.git
cd musteri-hizmetleri-chatbot
```

2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

3. `.env` dosyasını oluşturun:

```bash
python fix_paths.py
```

4. OpenAI API anahtarınızı `.env` dosyasına ekleyin:

```
OPENAI_API_KEY=your-api-key-here
```

## Kullanım

### Web Arayüzü

```bash
python run_web.py
```

Tarayıcınızda http://localhost:5000 adresini açın.

### Komut Satırı Arayüzü

```bash
python -m src.main
```

### Windows Kullanıcıları İçin

Doğrudan çalıştırmak için:

```bash
start_app.bat
```

## Proje Yapısı

```
├── data/                  # Veri dosyaları
│   └── reference/         # Referans Excel dosyaları
├── logs/                  # Log dosyaları
├── src/                   # Kaynak kodlar
│   ├── api/               # API entegrasyonları
│   ├── cli/               # Komut satırı arayüzü
│   ├── nlp/               # Doğal dil işleme modülleri
│   ├── utils/             # Yardımcı fonksiyonlar
│   ├── main.py            # Ana uygulama
│   └── web_app.py         # Web uygulaması
├── tests/                 # Test dosyaları
├── web/                   # Web arayüzü
│   ├── static/            # Statik dosyalar (CSS, JS)
│   └── templates/         # HTML şablonları
├── fix_paths.py           # Dosya yollarını düzenleme betiği
├── requirements.txt       # Gerekli paketler
├── run_app.py             # Uygulama başlatma betiği
├── run_web.py             # Web uygulaması başlatma betiği
└── start_app.bat          # Windows için başlatma dosyası
```

## Teknolojiler

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **NLP**: OpenAI GPT
- **Veri İşleme**: Pandas

## Geliştirme

Projeye katkıda bulunmak için aşağıdaki adımları izleyin:

1. Bu depoyu forklayın
2. Yeni bir özellik dalı oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Dalınıza push edin (`git push origin feature/amazing-feature`)
5. Pull Request gönderin

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Proje Sahibi - [@username](https://twitter.com/username) - email@example.com

Proje Linki: [https://github.com/username/musteri-hizmetleri-chatbot](https://github.com/username/musteri-hizmetleri-chatbot) 