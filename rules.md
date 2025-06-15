# 📜 ChatGPT Tabanlı Chatbot Projesi – Kodlama Kuralları (rules.md)

Bu dosya, ChatGPT destekli CLI tabanlı müşteri hizmetleri chatbotu geliştirirken izlenmesi gereken yapısal, güvenlik ve sürdürülebilirlik kurallarını içerir.

---

## 📁 1. Proje Dosya Yapısı

chatbot-project/
│
├── src/
│ ├── api/ # ChatGPT API çağrıları
│ ├── nlp/ # NLP ve ön işleme fonksiyonları
│ ├── cli/ # CLI arayüzü
│ ├── utils/ # Ortak yardımcı fonksiyonlar
│ └── main.py # Ana başlatıcı dosya
│
├── data/ # Log ve geçmiş verileri
├── .env # API anahtarı (gizli)
├── requirements.txt # Python bağımlılıkları
└── README.md # Proje tanıtımı


---

## 🔐 2. Güvenlik Kuralları

- API anahtarı `.env` dosyasında tutulmalı, kod içine gömülmemelidir.
- `.env` dosyası `.gitignore` içerisine eklenmelidir.
- Hassas bilgiler `os.getenv()` ile çekilmelidir.

---

## 🤖 3. ChatGPT API Kullanımı

- API istemcisi merkezi bir modülde (`api/chatgpt.py`) tanımlanmalı.
- API çağrıları `try-except` blokları ile güvenli hale getirilmelidir.
- Her API çağrısı için `prompt` ve `response` loglanmalıdır.

---

## 🧠 4. NLP ve Girdi İşleme

- Tüm kullanıcı girdileri normalize edilmelidir:
  - Küçük harfe çevirme
  - Boşlukları temizleme
- Gerekirse uygunsuz kelime filtresi eklenmelidir.
- Girdi işleme kodu `nlp/` altında olmalıdır.

---

## 🧑‍💻 5. CLI Arayüzü Kuralları

- Kullanıcı girdisi `input()` ile alınmalı.
- “çık”, “exit”, “quit” yazıldığında sistemden çıkılmalı.
- Boş mesajlar uyarı ile reddedilmelidir.
- Tüm CLI etkileşimi `cli/interface.py` dosyasında olmalıdır.

---

## 🧾 6. Loglama

- Her kullanıcı-bot konuşması `data/log.txt` dosyasına yazılmalıdır.
- Log formatı: `[timestamp] USER: …`, `[timestamp] BOT: …`
- Gerektiğinde JSON formatlı log da desteklenmelidir.

---

## 🧪 7. Test Kuralları

- `tests/` klasörü oluşturulmalı.
- `pytest` ile test edilebilirlik sağlanmalı.
- En azından aşağıdaki fonksiyonlar test edilmelidir:
  - Girdi işleme (preprocess)
  - API bağlantısı
  - CLI geçersiz giriş kontrolü

---

## 📌 8. Kod Standartları

- Her fonksiyon için açıklayıcı `docstring` kullanılmalıdır.
- Kod açıklamaları Türkçe olabilir, ancak teknik terimler İngilizce tutulmalıdır.
- Fonksiyon isimleri `snake_case`, sınıf isimleri `PascalCase` kullanılmalıdır.

---

## 🔄 9. Genişletilebilirlik ve Sürdürülebilirlik

- Kod modüler yapıda yazılmalı, her iş tek bir sorumluluğa sahip olmalıdır (SRP).
- ChatGPT dışında farklı LLM’ler entegre edilebilir yapıda olmalıdır.
- CLI yerine web arayüzü entegresi kolayca yapılabilecek şekilde yapılandırılmalıdır.

---

