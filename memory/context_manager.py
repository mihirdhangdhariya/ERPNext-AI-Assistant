import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings
import uuid
import json
import time
import os

class FAISSContextManager:
    def __init__(self, dim: int = 768, use_hnsw: bool = True):
        self.dim = dim
        self.context_data = []
        self.embedder = OpenAIEmbeddings(
            openai_api_key=os.getenv("TOGETHER_API_KEY"),
            openai_api_base="https://api.together.xyz/v1",
            model="togethercomputer/m2-bert-80M-2k-retrieval"
        )
        if use_hnsw:
            self.index = faiss.IndexHNSWFlat(dim, 16)
        else:
            self.index = faiss.IndexFlatL2(dim)

        print(f"✅ FAISS context manager initialized (dim={dim}, HNSW={use_hnsw})")

    def store_interaction(self, query: str, response: str, department: str) -> str:
        """
        Store a (query, response, department) pair in memory and FAISS.
        Truncates text to avoid embedding API errors.
        """
        if not response or len(response.strip()) < 10:
            return None

        # Truncate response to avoid embedding errors
        text_repr = f"Q: {query[:100]}\nA: {response[:200]}"
        text_repr_trunc = text_repr[:500]  # Safe length for embeddings
        
        vector = None
        embedding_success = False

        try:
            embedding = self.embedder.embed_query(text_repr_trunc)
            vector = np.array(embedding).astype('float32').reshape(1, -1)
            self.index.add(vector)
            embedding_success = True
        except Exception as e:
            print(f"⚠️ Embedding error: {str(e)}")
            # Fallback: add a zero vector for index alignment
            vector = np.zeros((1, self.dim), dtype='float32')
            self.index.add(vector)

        context_entry = {
            "id": str(uuid.uuid4()),
            "query": query[:200],
            "response": response[:500],  # Truncated response
            "department": department,
            "timestamp": int(time.time()),
            "text": text_repr_trunc,
            "embedding_success": embedding_success
        }
        self.context_data.append(context_entry)
        return context_entry["id"]

    def get_context(self, query: str, department: str, k: int = 2) -> list:
        """
        Retrieve the k most relevant context entries for a given query and department.
        """
        if len(self.context_data) == 0 or self.index.ntotal == 0:
            return []
        try:
            # Truncate query for embedding to avoid errors
            query_embedding = self.embedder.embed_query(query[:500])
            query_vector = np.array(query_embedding).astype('float32').reshape(1, -1)
        except Exception as e:
            print(f"⚠️ Query embedding error: {str(e)}")
            return []
        safe_k = min(k * 2, self.index.ntotal)
        if safe_k == 0:
            return []
        distances, indices = self.index.search(query_vector, safe_k)
        relevant_context = [
            {
                **self.context_data[idx],
                "distance": float(distance)
            }
            for idx, distance in zip(indices[0], distances[0])
            if 0 <= idx < len(self.context_data) and self.context_data[idx]["department"] == department
        ]
        relevant_context.sort(key=lambda x: x["distance"])
        return relevant_context[:k]

    def save_to_disk(self, path: str) -> bool:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            faiss.write_index(self.index, f"{path}.index")
            with open(f"{path}.json", "w") as f:
                json.dump(self.context_data, f)
            print(f"💾 Context saved to {path}.index|json")
            return True
        except Exception as e:
            print(f"⚠️ Save error: {str(e)}")
            return False

    def load_from_disk(self, path: str) -> bool:
        try:
            if os.path.exists(f"{path}.index"):
                self.index = faiss.read_index(f"{path}.index")
            if os.path.exists(f"{path}.json"):
                with open(f"{path}.json", "r") as f:
                    self.context_data = json.load(f)
            return True
        except Exception as e:
            print(f"⚠️ Load error: {str(e)}")
            return False

    def clear_memory(self):
        """Clear all in-memory context and FAISS index."""
        self.index.reset()
        self.context_data = []
        print("🧹 Context memory cleared")

    def get_context_stats(self) -> dict:
        """Return info about memory size and FAISS index."""
        return {
            "entries": len(self.context_data),
            "vectors": self.index.ntotal if hasattr(self.index, 'ntotal') else 0,
            "dimensions": self.dim
        }