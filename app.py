import streamlit as st
import os
import shutil
from src.agent import Agent
from src.data_loader import DataLoader
from src.text_processor import TextProcessor
from src.vectorstore import VectorDB

# --- AYARLAR ---
st.set_page_config(page_title="LocalMind AI", page_icon="🧠", layout="wide")

# Klasör İsimleri (Dosya yüklerken seçtirmek için)
UPLOAD_DIRS = {
    "Notlar": "data/notes",
    "SMS Geçmişi": "data/sms",
    "E-Postalar": "data/emails",
    "Çağrı Kayıtları": "data/calls"
}

# --- FONKSİYONLAR ---

def init_agent():
    """Agent'i başlatir ve session state'e kaydeder."""
    if "agent" not in st.session_state:
        st.session_state.agent = Agent()
        st.session_state.messages = [] # Sohbet geçmişi

def save_uploaded_file(uploaded_file, category):
    """Yüklenen dosyayi ilgili klasöre kaydeder."""
    target_dir = UPLOAD_DIRS[category]
    # Klasör yoksa oluştur
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def rebuild_database():
    """Veritabanını sıfırdan oluşturur (build_db.py mantığı)."""
    with st.status("Veritabanı güncelleniyor...", expanded=True) as status:
        st.write("📂 Veriler okunuyor...")
        loader = DataLoader()
        raw_docs = loader.load_all()
        
        st.write("✂️ Metinler parçalanıyor...")
        processor = TextProcessor()
        chunks = processor.split_documents(raw_docs)
        
        st.write("🔮 Vektörler oluşturuluyor (BERT)...")
        vec_db = VectorDB()
        vec_db.create_vector_db(chunks)
        
        status.update(label="✅ Veritabanı başarıyla güncellendi!", state="complete", expanded=False)

# --- ARAYÜZ TASARIMI ---

def main():
    st.title("🧠 LocalMind: Kişisel AI Asistanı")

    # 1. Yan Menü (Veri Yönetimi)
    with st.sidebar:
        st.header("📂 Veri Yönetimi")
        
        # Dosya Yükleme Kısmı
        st.subheader("Yeni Veri Ekle")
        category = st.selectbox("Veri Türü Seçin:", list(UPLOAD_DIRS.keys()))
        uploaded_files = st.file_uploader("Dosyaları Sürükleyin", accept_multiple_files=True)
        
        if uploaded_files and st.button("Dosyaları Kaydet"):
            for up_file in uploaded_files:
                save_uploaded_file(up_file, category)
            st.success(f"{len(uploaded_files)} dosya '{category}' klasörüne eklendi!")
        
        st.divider()
        
        # Veritabanı Güncelleme
        st.info("Yeni dosya ekledikten sonra veritabanını güncellemeyi unutmayın.")
        if st.button("🔄 Bilgi Tabanını Güncelle"):
            rebuild_database()
            # Agent'ı yeniden başlatmak gerekebilir (yeni veriyi görmesi için)
            st.session_state.agent = Agent() 
            st.rerun()

    # 2. Ana Sohbet Ekranı
    
    # Agent'ı yükle (Sadece bir kere çalışır)
    init_agent()

    # Geçmiş mesajları ekrana çiz
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcıdan girdi al
    if prompt := st.chat_input("Bir şeyler sorun... (Örn: Bugün randevum var mı?)"):
        # Kullanıcı mesajını ekrana bas ve kaydet
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Asistanın cevabını üret
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyorum..."):
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
        
        # Asistan mesajını kaydet
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()