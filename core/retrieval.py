"""
Echoes.exe — Evidence Retrieval Engine
Provides deterministic, TF-IDF grounded evidence search across extracted repository chunks.
Ensures the Ghost interview only answers with traceable citations.
"""
import re
import math
from typing import List, Dict, Any


class EvidenceRetriever:
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self._doc_tokens = [self._tokenize(c.get("content", "")) for c in chunks]
        self._df = {}
        for tokens in self._doc_tokens:
            for term in set(tokens):
                self._df[term] = self._df.get(term, 0) + 1
        self._num_docs = max(1, len(chunks))

    def _tokenize(self, text: str) -> List[str]:
        """Simple lowercase alphanumeric tokenization."""
        return re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant chunks using TF-IDF cosine approximation.
        Never fabricates or extrapolates missing evidence.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.chunks:
            # Fall back to first few general chunks (genesis, silence, manifest)
            return self.chunks[:top_k]

        scores = []
        for idx, doc_tokens in enumerate(self._doc_tokens):
            if not doc_tokens:
                scores.append(0.0)
                continue

            score = 0.0
            doc_len = len(doc_tokens)
            for q_term in query_tokens:
                tf = doc_tokens.count(q_term) / doc_len
                df = self._df.get(q_term, 0)
                idf = math.log((self._num_docs + 1) / (df + 1)) + 1.0
                score += tf * idf

            # Boost chunks that explicitly match citations or source types
            source = self.chunks[idx].get("source_type", "")
            if any(term in source for term in query_tokens):
                score *= 1.3

            scores.append(score)

        # Sort descending by score
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        results = []
        for i in ranked_indices[:top_k]:
            chunk_copy = dict(self.chunks[i])
            chunk_copy["relevance_score"] = round(scores[i], 4)
            results.append(chunk_copy)

        return results
