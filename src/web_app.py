"""
ChatBot Web Arayüzü Uygulaması
"""

import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

from .utils.config import Config
from .utils.logger import get_logger
from .api.chatgpt import ChatGPTIntegration
from .cli.interface import ChatInterface

logger = get_logger(__name__)

app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "web/templates"),
           static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "web/static"))

CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chatbot-secret-key-2024")
app.config['SESSION_TYPE'] = 'filesystem'

# Uygulama ayarlarını yükle
config = Config()

# ChatGPT entegrasyonu
chatgpt = ChatGPTIntegration(config)

# Chat arayüzü
chat_interface = ChatInterface(config)

@app.route('/')
def index():
    """Ana sayfa - Karşılama Sayfası"""
    return render_template('landing.html')

@app.route('/chat')
def chat():
    """Chat sayfası"""
    return render_template('chat.html')

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

@app.route('/api/reset', methods=['POST'])
def reset_chat():
    """Sohbeti sıfırla"""
    try:
        chatgpt.reset_conversation()
        return jsonify({"status": "success", "message": "Sohbet sıfırlandı"})
    except Exception as e:
        logger.error(f"Sıfırlama hatası: {str(e)}")
        return jsonify({"status": "error", "message": f"Hata: {str(e)}"}), 500

def start_web_app(debug=False, port=5000):
    """Web uygulamasını başlat"""
    logger.info(f"Web uygulaması başlatılıyor, port: {port}, debug: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    start_web_app(debug=True) 