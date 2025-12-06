from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

class TextProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Dokümanları daha küçük parçalara (chunk) böler."""
        chunks = self.splitter.split_documents(documents)
        print(f"✂️  {len(documents)} doküman -> {len(chunks)} parçaya bölündü.")
        return chunks