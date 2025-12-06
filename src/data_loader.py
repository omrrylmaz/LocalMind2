import json
import glob
import re
import os
from typing import List, Dict, Any
from pathlib import Path
from langchain_core.documents import Document
from src.config import DATA_DIR

class DataLoader:
    def __init__(self):
        self.data_path = DATA_DIR

    def load_all(self) -> List[Document]:
        """Tüm kaynaklardan veriyi ve METADATA'yı okur."""
        documents = []
        documents.extend(self._load_sms())
        documents.extend(self._load_emails())
        documents.extend(self._load_notes())
        documents.extend(self._load_calendar())
        documents.extend(self._load_calls())
        
        print(f"📚 Toplam {len(documents)} doküman ve metadata işlendi.")
        return documents

    def _extract_metadata_from_text(self, text: str, patterns: Dict[str, str]) -> Dict[str, str]:
        """Metin dosyasından Regex ile bilgi (Gönderen, Tarih vb.) çeker."""
        metadata = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
            else:
                metadata[key] = "Bilinmiyor"
        return metadata

    def _load_sms(self) -> List[Document]:
        docs = []
        path = self.data_path / "sms" / "*.json"
        for filepath in glob.glob(str(path)):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for sms in data:
                    # JSON zaten yapısal olduğu için direkt alıyoruz
                    meta = {
                        "source": "sms",
                        "sender": sms.get("from", "Bilinmiyor"),
                        "timestamp": sms.get("date", ""),
                        "subject": "SMS Mesajı" # SMS'te konu olmaz, genel atadık
                    }
                    text = f"SMS: {sms['content']}"
                    docs.append(Document(page_content=text, metadata=meta))
        return docs

    def _load_emails(self) -> List[Document]:
        docs = []
        path = self.data_path / "emails" / "*.txt"
        
        # E-posta başlıklarını yakalamak için Regex kalıpları
        patterns = {
            "sender": r"Kimden:\s*(.*)",
            "subject": r"Konu:\s*(.*)",
            "timestamp": r"Tarih:\s*(.*)"
        }

        for filepath in glob.glob(str(path)):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
                # Regex ile başlıkları çek
                meta = self._extract_metadata_from_text(text, patterns)
                meta["source"] = "email"
                
                # İçeriği temizle (Başlıkları metinden çıkarmak istersen burayı geliştirebiliriz)
                docs.append(Document(page_content=text, metadata=meta))
        return docs

    def _load_notes(self) -> List[Document]:
        docs = []
        path = self.data_path / "notes" / "*.txt"
        for filepath in glob.glob(str(path)):
            filename = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                # Notlarda gönderen kişinin kendisidir
                meta = {
                    "source": "note",
                    "sender": "Kullanıcı",
                    "subject": filename, # Dosya adını konu yaptık
                    "timestamp": "Güncel" # Dosya oluşturma tarihi de alınabilir
                }
                docs.append(Document(page_content=text, metadata=meta))
        return docs

    def _load_calendar(self) -> List[Document]:
        docs = []
        path = self.data_path / "calendar" / "*.json"
        for filepath in glob.glob(str(path)):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for event in data:
                    meta = {
                        "source": "calendar",
                        "sender": "Takvim",
                        "subject": event.get("event", "Etkinlik"),
                        "timestamp": event.get("date", ""),
                        "location": event.get("location", "")
                    }
                    text = f"Etkinlik: {event['event']} @ {event['location']}"
                    docs.append(Document(page_content=text, metadata=meta))
        return docs
    
    def _load_calls(self) -> List[Document]:
        docs = []
        path = self.data_path / "calls" / "*.txt"
        
        patterns = {
            "sender": r"Arayan:\s*(.*)",
            "timestamp": r"Tarih:\s*(.*)",
            "subject": r"Özet:\s*(.*)" # Çağrı özetini konu olarak alalım
        }

        for filepath in glob.glob(str(path)):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                meta = self._extract_metadata_from_text(text, patterns)
                meta["source"] = "call_log"
                
                docs.append(Document(page_content=text, metadata=meta))
        return docs

if __name__ == "__main__":
    loader = DataLoader()
    docs = loader.load_all()
    # Örnek bir dokümanın Metadata'sını görelim
    print(f"\n🔎 Örnek Metadata İncelemesi:")
    print(docs[0].metadata)