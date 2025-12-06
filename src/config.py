import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje ana dizini (src'nin bir üstü)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Model Ayarları
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
REPO_ID = os.getenv("REPO_ID", "Trendyol/LLaMa-v3-8b-chat-v0.1")

# Vektör Veritabanı Ayarları
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

if not HF_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN bulunamadı! .env dosyasını kontrol et.")