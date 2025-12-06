from typing import List, Optional, Dict
from langchain_core.documents import Document
from src.vectorstore import VectorDB

class RAGEngine:
    def __init__(self):
        self.vector_db_instance = VectorDB()
        self.vectorstore = self.vector_db_instance.get_vectorstore()

    def _format_filter(self, meta_filter: Optional[Dict]) -> Optional[Dict]:
        """
        ChromaDB için filtre formatını düzeltir.
        Örn: {'source': 'email', 'sender': 'patron'} 
        --> {'$and': [{'source': 'email'}, {'sender': 'patron'}]}
        """
        if not meta_filter:
            return None
        
        # Eğer filtrede birden fazla kriter varsa (örn: source VE sender)
        if len(meta_filter) > 1:
            return {
                "$and": [{key: value} for key, value in meta_filter.items()]
            }
        
        # Tek kriter varsa olduğu gibi döndür
        return meta_filter

    def retrieve(self, query: str, meta_filter: Optional[Dict] = None, k: int = 5) -> List[Document]:
        
        # Filtreyi Chroma formatına çevir
        chroma_filter = self._format_filter(meta_filter)
        
        print(f"🔍 Motor Çalışıyor -> Sorgu: '{query}' | Ham Filtre: {meta_filter} | Chroma Filtre: {chroma_filter}")
        
        try:
            docs = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=chroma_filter
            )
            print(f"📄 {len(docs)} adet doküman bulundu.")
            return docs
        except Exception as e:
            print(f"⚠️ Arama hatası: {e}")
            return []