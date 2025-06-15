document.addEventListener('DOMContentLoaded', () => {
    // DOM Elementleri
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const sectorRadios = document.querySelectorAll('input[name="sectorRadio"]');
    const chatSection = document.getElementById('chatSection');

    // Değişkenler
    let activeSector = 'all';
    let isWaitingForResponse = false;
    let isFirstUserMessage = true;
    let welcomeMessageShown = false;

    // Sektöre özgü karşılama mesajları
    const welcomeMessages = {
        all: "Merhaba! Ben müşteri hizmetleri asistanınız. Size havalimanı, kargo veya restoran hizmetleriyle ilgili konularda yardımcı olabilirim. Nasıl yardımcı olabilirim?",
        havalimani: "Merhaba! Havalimanı hizmetleri asistanıyım. Uçuş bilgileri, bagaj takibi veya diğer havalimanı hizmetleri hakkında sorularınızı yanıtlayabilirim. Size nasıl yardımcı olabilirim?",
        kargo: "Merhaba! Kargo takip asistanıyım. Gönderinizin durumu, teslimat süresi veya diğer kargo hizmetleri hakkında bilgi almak için bana sorabilirsiniz. Size nasıl yardımcı olabilirim?",
        restoran: "Merhaba! Restoran hizmetleri asistanıyım. Rezervasyon, sipariş takibi veya menü bilgileri hakkında size yardımcı olabilirim. Bugün nasıl yardımcı olabilirim?"
    };

    // Başlangıç karşılama mesajını ekle (sadece bir kez)
    if (!welcomeMessageShown) {
        addWelcomeMessage(activeSector);
        welcomeMessageShown = true;
    }

    // Sayfa yüklendiğinde efekt ekle
    animateParticles();
    
    // Kullanıcıya odaklan
    setTimeout(() => {
        userInput.focus();
    }, 1000);

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    newChatBtn.addEventListener('click', resetChat);

    // Sektör seçimi değiştiğinde
    sectorRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const previousSector = activeSector;
            activeSector = e.target.value;
            console.log(`Aktif sektör: ${activeSector}`);
            
            // Seçim animasyonu
            const label = e.target.nextElementSibling;
            animateElement(label);
            
            // Sektör değiştiğinde yeni karşılama mesajı ekle
            if (previousSector !== activeSector) {
                resetChat(false);
            }
        });
    });

    // Fonksiyonlar
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

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        
        // Avatar içeriği
        const avatarIcon = document.createElement('i');
        avatarIcon.className = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        avatarDiv.appendChild(avatarIcon);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = `<p>${formatMessage(content)}</p>`;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getCurrentTime();

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        
        // Animasyon efekti ekle
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
        
        // Otomatik scroll
        scrollToBottom();
    }

    function addWelcomeMessage(sector) {
        // Sektöre göre karşılama mesajını belirle
        const welcomeMsg = welcomeMessages[sector] || welcomeMessages.all;
        addMessage(welcomeMsg, 'bot');
    }

    function addTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'message bot-message typing-indicator';
        indicatorDiv.id = 'typingIndicator';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        
        const avatarIcon = document.createElement('i');
        avatarIcon.className = 'fas fa-robot';
        avatarDiv.appendChild(avatarIcon);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = '<p>Yazıyor<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></p>';

        contentDiv.appendChild(textDiv);
        indicatorDiv.appendChild(avatarDiv);
        indicatorDiv.appendChild(contentDiv);

        chatMessages.appendChild(indicatorDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function fetchBotResponse(message, sector) {
        // API isteği
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                sector: sector
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Yazıyor göstergesini kaldır
            removeTypingIndicator();
            
            // Chatbot yanıtını ekle
            if (data.status === 'success') {
                // Kısa bir gecikme ekleyerek daha gerçekçi bir deneyim sun
                setTimeout(() => {
                    addMessage(data.message, 'bot');
                }, 500);
            } else {
                setTimeout(() => {
                    addMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'bot');
                }, 500);
                console.error('API Hatası:', data);
            }
            
            // Bekleme durumunu kaldır
            isWaitingForResponse = false;
        })
        .catch(error => {
            console.error('Bağlantı hatası:', error);
            removeTypingIndicator();
            setTimeout(() => {
                addMessage('Üzgünüm, bir bağlantı hatası oluştu. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.', 'bot');
            }, 500);
            isWaitingForResponse = false;
        });
    }

    function resetChat(showConfirm = true) {
        // Onay mesajı göster
        if (showConfirm && !confirm('Sohbeti sıfırlamak istediğinizden emin misiniz? Tüm konuşma geçmişi silinecektir.')) {
            return; // Kullanıcı iptal ettiyse işlemi durdur
        }
        
        // Mesajları temizle
        chatMessages.innerHTML = '';
        
        // İlk mesaj durumunu sıfırla
        isFirstUserMessage = true;
        
        // Yeni karşılama mesajı ekle
        addWelcomeMessage(activeSector);
        
        // API'ye reset isteği gönder
        fetch('/api/reset', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            console.log('Sohbet sıfırlandı:', data);
        })
        .catch(error => {
            console.error('Sıfırlama hatası:', error);
        });
    }

    function getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    function scrollToBottom() {
        // Smooth scrolling to bottom
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    function formatMessage(text) {
        // Takip kodlarını vurgula (TR ile başlayan ve rakamlarla devam eden)
        text = text.replace(/\b(TR\d{6,12})\b/gi, '<span class="highlight-code">$1</span>');
        
        // Uçuş kodlarını vurgula (2 harf ve 3-4 rakam)
        text = text.replace(/\b([A-Z]{2}\d{3,4})\b/g, '<span class="highlight-code">$1</span>');
        
        // Linkleri vurgula
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="chat-link">$1</a>');
        
        return text;
    }
    
    function addWelcomeEffect() {
        // Seçili sektörü vurgula
        const activeRadio = document.querySelector('input[name="sectorRadio"]:checked');
        if (activeRadio) {
            const label = activeRadio.nextElementSibling;
            animateElement(label);
        }
    }
    
    function animateElement(element) {
        element.classList.add('animate-pulse');
        setTimeout(() => {
            element.classList.remove('animate-pulse');
        }, 1000);
    }
    
    function animateParticles() {
        const particles = document.querySelectorAll('.particle');
        particles.forEach(particle => {
            const randomX = Math.random() * window.innerWidth;
            const randomY = Math.random() * window.innerHeight;
            particle.style.transform = `translate(${randomX}px, ${randomY}px)`;
        });
    }

    // CSS için ek stil
    const style = document.createElement('style');
    style.textContent = `
        .typing-indicator .dot {
            animation: typing 1.5s infinite;
            display: inline-block;
        }
        .typing-indicator .dot:nth-child(2) {
            animation-delay: 0.5s;
        }
        .typing-indicator .dot:nth-child(3) {
            animation-delay: 1s;
        }
        @keyframes typing {
            0%, 100% { opacity: 0.2; }
            50% { opacity: 1; }
        }
        .highlight-code {
            color: #6c5ce7;
            font-weight: 500;
            background: rgba(108, 92, 231, 0.1);
            padding: 2px 5px;
            border-radius: 4px;
        }
        .chat-link {
            color: #4C6EF5;
            text-decoration: underline;
        }
        .animate-pulse {
            animation: pulse-animation 1s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        @keyframes pulse-animation {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
}); 