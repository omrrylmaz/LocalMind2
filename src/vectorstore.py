import os
import shutil
# DİKKAT: embedding sınıfı değişti
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List
from src.config import CHROMA_PERSIST_DIR

class VectorDB:
    def __init__(self):
        print("🇹🇷 Türkçe BERT Embedding Modeli Yükleniyor...")
        # İŞTE İSTEDİĞİN TÜRKÇE BERT MODELİ BURADA:
        # Bu model cümleleri Türkçe mantığına göre vektöre çevirir.
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
        )
        self.persist_directory = str(CHROMA_PERSIST_DIR)

    def create_vector_db(self, documents: List[Document]):
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            print(f"🧹 Eski veritabanı temizlendi.")

        print("🔮 Türkçe vektörler oluşturuluyor... (Biraz sürebilir)")
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embedding_model,
            persist_directory=self.persist_directory
        )
        print(f"💾 Veritabanı hazır: {self.persist_directory}")
        return vectorstore

    def get_retriever(self):
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # src/vectorstore.py içine eklenecek metod:
    def get_vectorstore(self):
        """Mevcut veritabanı nesnesini döndürür."""
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )