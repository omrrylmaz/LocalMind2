from src.data_loader import DataLoader
from src.text_processor import TextProcessor
from src.vectorstore import VectorDB
import time

def main():
    start_time = time.time()
    
    print("🚀 Bilgi Tabanı Oluşturma Başladı...")

    # 1. ADIM: Verileri Oku
    print("\n--- Adım 1: Veri Yükleme ---")
    loader = DataLoader()
    raw_docs = loader.load_all()

    # 2. ADIM: Verileri Parçala (Chunking)
    print("\n--- Adım 2: Metin İşleme ---")
    processor = TextProcessor()
    chunks = processor.split_documents(raw_docs)

    # 3. ADIM: Vektör Veritabanına Yaz
    print("\n--- Adım 3: Vektör Kaydı ---")
    vec_db = VectorDB()
    vec_db.create_vector_db(chunks)

    elapsed = time.time() - start_time
    print(f"\n✅ İşlem Tamamlandı! Toplam Süre: {elapsed:.2f} saniye.")

if __name__ == "__main__":
    main()