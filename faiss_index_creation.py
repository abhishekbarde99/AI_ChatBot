from sentence_transformers import SentenceTransformer, util
from docx import Document
import faiss
import numpy as np

class Document_Handling:

    def __init__(self):
        self.input_file = "./Input/Python_DSA_Tutorial.docx"
        # Sentence Transformer model
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    def document_text(self):
        # Corpus of documents
        doc = Document(self.input_file)
        return [para.text for para in doc.paragraphs if para.text.strip()]

    # Function to create FAISS index
    def create_faiss_index(self):
        # Corpus of documents and their embeddings
        corpus = self.document_text()
        corpus_embeddings = self.model.encode(corpus, convert_to_tensor=False)  # Convert text to vectors
        index = faiss.IndexFlatL2(corpus_embeddings.shape[1])  # L2 distance index
        index.add(np.array(corpus_embeddings, dtype=np.float32))  # Add embeddings to FAISS
        faiss.write_index(index,"./Input/document_faiss_index.idx")

# Document_Handling().create_faiss_index()