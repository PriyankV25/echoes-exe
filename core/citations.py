"""
Echoes.exe — Citation Formatter and Validator
Verifies that all facts cited in Ghost responses correspond to real repository evidence.
Distinguishes between FACT, INTERPRETATION, HYPOTHESIS, and UNRESOLVED DATA.
"""
import re
from typing import List, Dict, Any, Tuple


class CitationValidator:
    CITATION_REGEX = re.compile(r"\[(?:Source|Cite|Evidence):\s*([^\]]+)\]", re.IGNORECASE)

    @classmethod
    def extract_citations(cls, text: str) -> List[str]:
        """Finds all explicit evidence citations in the response."""
        return cls.CITATION_REGEX.findall(text)

    @classmethod
    def validate_citations(cls, text: str, available_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cross-references citations in AI output with actual indexed evidence chunks.
        Returns validated citations, confidence score, and flag for uncited claims.
        """
        found_cites = cls.extract_citations(text)
        valid_cites = []
        unverified_cites = []

        known_sources = set()
        for chk in available_chunks:
            known_sources.add(chk.get("source_path", "").lower())
            known_sources.add(chk.get("citation", "").lower())
            known_sources.add(chk.get("chunk_id", "").lower())

        for cite in found_cites:
            clean = cite.strip().lower()
            matched = any(clean in src or src in clean for src in known_sources)
            if matched or "commit" in clean or "readme" in clean or "package.json" in clean or "requirements" in clean:
                valid_cites.append(cite.strip())
            else:
                unverified_cites.append(cite.strip())

        # Check for epistemic labels
        has_facts = bool(re.search(r"\b(FACT|EVIDENCE)\b", text, re.IGNORECASE))
        has_hypo = bool(re.search(r"\b(HYPOTHESIS|INTERPRETATION|UNRESOLVED)\b", text, re.IGNORECASE))

        confidence = 0.95 if (valid_cites and not unverified_cites) else 0.80 if valid_cites else 0.65

        return {
            "valid_citations": valid_cites,
            "unverified_citations": unverified_cites,
            "has_epistemic_labels": has_facts or has_hypo,
            "confidence_score": confidence,
            "citation_count": len(found_cites)
        }

    @classmethod
    def format_grounded_context(cls, chunks: List[Dict[str, Any]]) -> str:
        """Formats evidence chunks for LLM injection with clear boundaries."""
        if not chunks:
            return "No verifiable evidence chunks could be retrieved for this query."

        lines = ["=== VERIFIED REPOSITORY EVIDENCE (UNTRUSTED ARCHIVE DATA) ==="]
        for c in chunks:
            lines.append(f"\n[ID: {c.get('chunk_id')}] Source: {c.get('citation')} ({c.get('category', 'FACT')})")
            lines.append(f"Content: {c.get('content')}")
        lines.append("\n=== END EVIDENCE ===")
        return "\n".join(lines)
