from __future__ import annotations

import json
import os
from typing import List

import faiss
import numpy as np
from ollama import Client

from app.core.config import settings


class RetrieverService:
    def __init__(self) -> None:
        self.client = Client(host=settings.ollama_base_url)
        self.embed_model = settings.ollama_embed_model
        self.dimension = settings.vector_dimension
        self.index_path = settings.faiss_index_path
        self.metadata_path = settings.faiss_metadata_path
        self.documents: list[str] = self._load_documents()
        self.index = self._load_or_create_index()

        if self.index.d != self.dimension:
            raise ValueError(
                f"Configured VECTOR_DIMENSION={self.dimension} does not match FAISS index dimension={self.index.d}."
            )

        if self.index.ntotal != len(self.documents):
            raise ValueError(
                "FAISS index and metadata are out of sync. Remove data files or repair metadata."
            )

    def _load_or_create_index(self) -> faiss.Index:
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        return faiss.IndexFlatL2(self.dimension)

    def _load_documents(self) -> list[str]:
        if not os.path.exists(self.metadata_path):
            return []

        with open(self.metadata_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        docs: list[str] = []
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                docs.append(item["text"])
        return docs

    def _save_documents(self) -> None:
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        payload = [{"text": doc} for doc in self.documents]
        with open(self.metadata_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=True, indent=2)

    def save_index(self) -> None:
        faiss.write_index(self.index, self.index_path)

    def _embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype="float32")

        try:
            # Current Ollama Python client API.
            response = self.client.embed(model=self.embed_model, input=texts)
            embeddings = response["embeddings"]
        except (AttributeError, TypeError):
            # Backward-compatible API.
            embeddings = [self.client.embeddings(model=self.embed_model, prompt=text)["embedding"] for text in texts]

        vectors = np.array(embeddings, dtype="float32")
        if vectors.ndim == 1:
            vectors = np.expand_dims(vectors, axis=0)

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch: got {vectors.shape[1]}, expected {self.dimension}."
            )

        return vectors

    def add_documents(self, docs: list[str]) -> None:
        clean_docs = [doc.strip() for doc in docs if doc and doc.strip()]
        if not clean_docs:
            return

        vectors = self._embed_texts(clean_docs)
        self.index.add(vectors)
        self.documents.extend(clean_docs)
        self.save_index()
        self._save_documents()

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            return []

        query_vector = self._embed_texts([query])
        _, indices = self.index.search(query_vector, top_k)

        results: list[str] = []
        for idx in indices[0]:
            if idx == -1:
                continue
            if idx < len(self.documents):
                results.append(self.documents[idx])

        return results

    def stats(self) -> dict[str, int]:
        return {
            "index_size": self.index.ntotal,
            "metadata_count": len(self.documents),
        }
