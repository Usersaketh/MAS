from __future__ import annotations

import os
from typing import List

import faiss
import numpy as np

from app.core.config import settings


class RetrieverService:
    def __init__(self) -> None:
        self.dimension = settings.vector_dimension
        self.index_path = settings.faiss_index_path
        self.documents: list[str] = []
        self.index = self._load_or_create_index()

    def _load_or_create_index(self) -> faiss.Index:
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        return faiss.IndexFlatL2(self.dimension)

    def save_index(self) -> None:
        faiss.write_index(self.index, self.index_path)

    def _embed(self, text: str) -> np.ndarray:
        # Placeholder embedding implementation for Stage 1.
        seed = abs(hash(text)) % (10**6)
        rng = np.random.default_rng(seed)
        vector = rng.random(self.dimension).astype("float32")
        return vector

    def add_documents(self, docs: list[str]) -> None:
        vectors = np.array([self._embed(doc) for doc in docs], dtype="float32")
        self.index.add(vectors)
        self.documents.extend(docs)
        self.save_index()

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([self._embed(query)], dtype="float32")
        _, indices = self.index.search(query_vector, top_k)

        results: list[str] = []
        for idx in indices[0]:
            if idx == -1:
                continue
            if idx < len(self.documents):
                results.append(self.documents[idx])

        return results
