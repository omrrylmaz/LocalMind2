
#  LocalMind: Kişisel Agentik RAG Asistanı

Bu proje, yerel dosya verilerini (SMS, e-posta, notlar, takvim) kullanarak çalışabilen, halüsinasyonları en aza indirilmiş, akıllı bir **Agentik Retrieval-Augmented Generation (RAG)** asistanının minimalist bir uygulamasını içerir.

Sistem, basit anahtar kelime araması yapmak yerine, kullanıcının niyetini (Örn: "Mail mi, SMS mi?") anlayarak veritabanında **filtreli ve yönlendirilmiş (Routed)** arama yapar.

---

##  Mimarinin Çalışma Mantığı (Advanced RAG)

Projemiz, geleneksel RAG sistemlerinin aksine, veritabanına sorgu göndermeden önce yapay zekayı bir **"Router" (Yönlendirici)** olarak kullanır. Bu sayede sadece aranan konuyla ilgili dosyalara bakılır, böylece cevaplar temizlenir ve halüsinasyon riski ortadan kalkar.

1.  **Veri Mühendisliği ve Metadata (Türkçe BERT):**
    * **Görevi:** Veriyi etiketlemek ve vektörlemek.
    * **İşleyiş:** `src/data_loader.py`, `/data` klasöründeki her dosyayı okur ve metin içeriğiyle birlikte `sender` (Gönderen), `source` (Kaynak tipi), `timestamp` gibi **Metadata** (üstveri) etiketlerini çıkarır.
    * **Teknoloji:** **Türkçe için eğitilmiş BERT** modeli, bu metinleri daha anlamlı vektörlere çevirir ve sonuçlar ChromaDB'ye bu etiketlerle kaydedilir.

2.  **Router Kararı (Agentic Routing):**
    * **Görevi:** Kullanıcı sorusunu analiz edip bir **arama emri** vermek.
    * **İşleyiş:** `src/agent.py` içindeki LLM (Qwen/Hugging Face) ilk olarak, sadece filtreleri ve aranacak anahtar kelimeyi içeren bir **JSON** çıktısı üretmeye zorlanır. *Örnek: Kullanıcı "Patrondan gelen mailler" dediğinde, JSON çıktısı `{"source": "email", "sender": "patron@sirket.com"}` olur.* 



3.  **Akıllı Arama (Filtreli Retrieval):**
    * **Görevi:** Yönlendiriciden gelen filtreyi veritabanına uygulamak.
    * **İşleyiş:** `src/rag_engine.py` modülü, LLM'den gelen JSON'u okur. Eğer birden fazla kriter varsa, bunları ChromaDB'nin anlayacağı **`$and` operatörüne** çevirir. Bu, veritabanında **SQL `WHERE`** cümlesi kullanmaya benzer bir hassasiyet sağlar. Sadece kritik veriler çekilir.

4.  **Nihai Cevap Üretimi:**
    * **Görevi:** Filtrelenmiş bağlamı kullanarak cevabı oluşturmak.
    * **İşleyiş:** Sadece (3) adımından gelen, küçük, temiz ve ilgili metin parçacıkları LLM'e sunulur. Model, kendisine verilen katı prompt talimatlarına uyarak (uydurma yapma, kısa cevap ver) nihai Türkçe cevabı kullanıcıya iletir.

---

##  Kurulum ve Çalıştırma

### 1. Ön Gereksinimler

* Python 3.9+
* Git (isteğe bağlı, projeyi kopyalamak için)
* Hugging Face **Read** (Okuma) yetkili **API Token**.

### 2. Ortam Kurulumu

Projeyi kopyalayın, sanal ortamı oluşturun ve bağımlılıkları yükleyin:

```bash


# Projeyi oluşturduğunuz dizine gidin
cd personal_ai_agent 


### env oluşturma 
python -m venv venv 

# Sanal ortamı etkinleştirin (venv)
.\venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# verileri etiketlemek için 
python build_db.py

# sohbet baslatma 
python main.py

# arayuz uzerinden sohbet 
streamlint app.
