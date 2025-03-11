from sentence_transformers import SentenceTransformer, util
from docx import Document
import faiss
import numpy as np

class Document_Handling:

    def __init__(self):
        self.input_file = "./Input/Python_DSA_Tutorial.docx"
        # Sentence Transformer model
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = faiss.read_index("./Input/document_faiss_index.idx")

    def document_text(self):
        # Corpus of documents
        doc = Document(self.input_file)
        return [para.text for para in doc.paragraphs if para.text.strip()]



    # Function to search for the closest match in FAISS
    def search_faiss_index(self,user_query, threshold=0.7):

        query_embedding = self.model.encode(user_query, convert_to_tensor=False).reshape(1, -1)

        # Search FAISS index
        D, I = self.index.search(query_embedding, 1)  # Get the best match

        best_match_score = 1 - (D[0][0] / 2)  # Convert L2 distance to similarity score
        best_match_idx = I[0][0]

        text_data = self.document_text()

        if best_match_score >= threshold:
            return text_data[best_match_idx], best_match_score
        return None, best_match_score
