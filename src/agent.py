import json
import datetime
from huggingface_hub import InferenceClient
from src.config import HF_TOKEN, REPO_ID
from src.rag_engine import RAGEngine

class Agent:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.client = InferenceClient(token=HF_TOKEN)
        self.model_id = REPO_ID

    def _get_current_date(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _decide_search_params(self, user_query: str) -> dict:
        """
        ADIM 1: ROUTER (Yönlendirici)
        Kullanıcının niyetini anlar ve filtreleri çıkarır.
        """
        today = self._get_current_date()
        
        # Router için özel prompt. Modele JSON konuşmayı öğretiyoruz.
        system_prompt = f"""Sen bir Veritabanı Uzmanısın. Görevin, kullanıcının sorusunu analiz edip arama parametreleri çıkarmaktır.
        Bugünün tarihi: {today}
        
        MEVCUT KAYNAKLAR (source): ['email', 'sms', 'note', 'call_log', 'calendar']
        
        KURALLAR:
        1. Sadece geçerli bir JSON objesi döndür. Başka hiçbir metin yazma.
        2. JSON formatı şöyle olmalı:
           {{
             "search_query": "Aranacak anahtar kelimeler",
             "filter": {{ "source": "kaynak_tipi", "sender": "gönderen_ismi" }}
           }}
        3. Eğer belirli bir gönderen yoksa 'sender' alanını ekleme.
        4. Eğer belirli bir kaynak yoksa 'filter' boş olabilir veya 'source' belirtmeyebilirsin.
        5. Kullanıcı 'mailler' derse source='email', 'mesajlar' derse source='sms', 'aramalar' derse source='call_log' yap.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Soru: {user_query}"}
        ]

        try:
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=150,
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            
            # Bazen model Markdown ```json ... ``` etiketi ekler, temizleyelim
            content = content.replace("```json", "").replace("```", "")
            
            params = json.loads(content)
            print(f"🧠 Router Kararı: {params}")
            return params
        except Exception as e:
            print(f"⚠️ Router hatası: {e}. Varsayılan arama yapılıyor.")
            return {"search_query": user_query, "filter": None}

    def chat(self, user_query: str) -> str:
        # --- AŞAMA 1: Niyet Analizi (Routing) ---
        search_params = self._decide_search_params(user_query)
        
        query_text = search_params.get("search_query", user_query)
        meta_filter = search_params.get("filter", None)

        # --- AŞAMA 2: Filtreli Arama (Retrieval) ---
        print(f"🚀 Veritabanına Gidiliyor -> Filtre: {meta_filter}")
        relevant_docs = self.rag_engine.retrieve(query_text, meta_filter=meta_filter)
        
        # --- AŞAMA 3: Cevap Üretme (Generation) ---
        context_text = "\n".join([f"- [{doc.metadata.get('source', 'genel')}] {doc.page_content}" for doc in relevant_docs])
        
        if not context_text:
            return "Kriterlerinize uygun bir kayıt bulamadım."

        messages = [
            {
                "role": "system",
                "content": f"""Sen LocalMind asistanısın. Aşağıdaki verileri kullanarak soruya Türkçe cevap ver.
                Veriler, kullanıcının kendi kişisel kayıtlarıdır (SMS, Mail vb.).
                
                VERİLER:
                {context_text}
                """
            },
            {
                "role": "user",
                "content": user_query
            }
        ]

        try:
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=300,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Model hatası: {e}"