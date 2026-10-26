"""
Information Retrieval (IR) Engine
- Custom Tokenizer & Normalizer (Arabic & English support)
- Inverted Index construction from text documents
- TF-IDF weight computation (smooth IDF)
- Cosine Similarity ranking
"""

import math
import os
import re
from typing import Dict, List, Tuple, Any

# Arabic stopwords list
ARABIC_STOPWORDS = {
    "في", "من", "على", "إلى", "عن", "مع", "هذا", "هذه", "ذلك", "تلك", "التي", "الذي",
    "الذين", "اللاتي", "هو", "هي", "هم", "هن", "أنت", "أنتم", "نحن", "أنا", "كان",
    "كانت", "يكون", "تكون", "أن", "إن", "ما", "لا", "لم", "لن", "قد", "كل", "أو",
    "ثم", "إذا", "حيث", "بين", "كما", "حتى", "غير", "فقط", "أي", "عند", "له", "لها",
    "لهم", "به", "بها", "بهم", "فيه", "فيها", "منه", "منها", "عنه", "عنها", "عليه", "عليها"
}

# English stopwords list
ENGLISH_STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "is", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "can", "could", "should", "would", "will",
    "it", "its", "this", "that", "these", "those", "we", "you", "they", "i", "he", "she"
}

STOPWORDS = ARABIC_STOPWORDS | ENGLISH_STOPWORDS


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text: remove diacritics, unify alef, ta-marbuta, and alef maqsura."""
    # Remove Tashkeel (diacritics)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    # Remove Tatweel (kashida)
    text = re.sub(r'\u0640', '', text)
    # Unify Alef
    text = re.sub(r'[إأآا]', 'ا', text)
    # Unify Ya / Alef Maqsura
    text = re.sub(r'ى', 'ي', text)
    # Unify Ta Marbuta / Ha
    text = re.sub(r'ة', 'ه', text)
    return text


def light_stem_arabic(word: str) -> str:
    """Light Arabic stemmer removing common prefixes and suffixes."""
    # Prefixes: ال, كال, بال, فال, ول
    if word.startswith("ال") and len(word) > 4:
        word = word[2:]
    elif (word.startswith("كال") or word.startswith("بال") or word.startswith("فال") or word.startswith("وال")) and len(word) > 5:
        word = word[3:]
    elif (word.startswith("و") or word.startswith("ف") or word.startswith("ب") or word.startswith("ل")) and len(word) > 4:
        word = word[1:]
    
    # Suffixes: ات, ون, ين, هم, هن, ها, نا
    for suf in ("ات", "ون", "ين", "هم", "هن", "ها", "نا", "ية"):
        if word.endswith(suf) and len(word) > len(suf) + 2:
            word = word[:-len(suf)]
            break
    return word


def tokenize(text: str) -> List[str]:
    """Tokenize and preprocess both Arabic and English text."""
    text = normalize_arabic(text.lower())
    # Match alphanumeric words (both latin and arabic unicode ranges)
    raw_tokens = re.findall(r'[\w]+', text)
    tokens = []
    for token in raw_tokens:
        if token in STOPWORDS or len(token) <= 1:
            continue
        # Apply light Arabic stemming if token contains arabic letters
        if re.search(r'[\u0600-\u06FF]', token):
            token = light_stem_arabic(token)
        tokens.append(token)
    return tokens


class Document:
    def __init__(self, doc_id: str, title: str, text: str, source_file: str):
        self.doc_id = doc_id
        self.title = title
        self.text = text
        self.source_file = source_file
        self.tokens: List[str] = tokenize(f"{title} {text}")
        self.length = len(self.tokens)
        self.term_freqs: Dict[str, int] = {}
        for token in self.tokens:
            self.term_freqs[token] = self.term_freqs.get(token, 0) + 1


class InvertedIndex:
    def __init__(self):
        # term -> {doc_id: raw_count}
        self.index: Dict[str, Dict[str, int]] = {}
        # doc_id -> Document
        self.documents: Dict[str, Document] = {}
        # doc_id -> norm of TF-IDF vector
        self.doc_vector_norms: Dict[str, float] = {}
        # term -> idf
        self.idf: Dict[str, float] = {}
        self.total_docs: int = 0

    def add_document(self, doc_id: str, title: str, text: str, source_file: str):
        """Add a single document to the collection and update the inverted index."""
        doc = Document(doc_id, title, text, source_file)
        self.documents[doc_id] = doc
        for term, count in doc.term_freqs.items():
            if term not in self.index:
                self.index[term] = {}
            self.index[term][doc_id] = count

    def build(self):
        """Compute IDFs and document TF-IDF vector norms."""
        self.total_docs = len(self.documents)
        if self.total_docs == 0:
            return

        # Compute smooth IDF: ln((N + 1) / (DF + 1)) + 1
        self.idf.clear()
        for term, postings in self.index.items():
            df = len(postings)
            self.idf[term] = math.log((self.total_docs + 1.0) / (df + 1.0)) + 1.0

        # Compute document TF-IDF vectors and their Euclidean norms
        self.doc_vector_norms.clear()
        for doc_id, doc in self.documents.items():
            norm_sq = 0.0
            doc_len = max(doc.length, 1)
            for term, count in doc.term_freqs.items():
                tf = count / doc_len
                tfidf = tf * self.idf.get(term, 1.0)
                norm_sq += tfidf * tfidf
            self.doc_vector_norms[doc_id] = math.sqrt(norm_sq) if norm_sq > 0 else 1.0

    def load_from_directory(self, docs_directory: str):
        """
        Loads all .txt files from docs_directory.
        Breaks large texts into meaningful sections/articles/courses for high retrieval precision.
        """
        self.index.clear()
        self.documents.clear()

        if not os.path.exists(docs_directory):
            raise FileNotFoundError(f"Directory not found: {docs_directory}")

        for filename in sorted(os.listdir(docs_directory)):
            if not filename.endswith(".txt"):
                continue
            filepath = os.path.join(docs_directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Split content into logical sections (by headers, "مادة", "[CODE]", or blank lines)
            sections = self._split_into_sections(content, filename)
            for sec_id, title, sec_text in sections:
                self.add_document(sec_id, title, sec_text, filename)

        # Also load and index faqs.json if present in parent data directory
        parent_dir = os.path.dirname(docs_directory)
        faqs_path = os.path.join(parent_dir, "faqs.json")
        if os.path.exists(faqs_path):
            try:
                import json
                with open(faqs_path, "r", encoding="utf-8") as f:
                    faqs_data = json.load(f)
                    for item in faqs_data:
                        f_id = item.get("id", "faq")
                        q_ar = item.get("question", "")
                        q_en = item.get("question_en", "")
                        ans = item.get("answer", "")
                        self.add_document(
                            doc_id=f"faq_{f_id}",
                            title=f"سؤال شائع: {q_ar}",
                            text=f"{q_ar}\n{q_en}\nالإجابة: {ans}",
                            source_file="faqs.json"
                        )
            except Exception:
                pass

        self.build()

    def _split_into_sections(self, content: str, filename: str) -> List[Tuple[str, str, str]]:
        """Splits document content into indexed passages based on structure."""
        sections = []
        lines = content.strip().split("\n")
        current_title = filename
        current_lines = []
        sec_counter = 1

        for line in lines:
            trimmed = line.strip()
            # Detect section break like 'مادة (X)' or '[CODE]' or '1. الأستاذ'
            is_header = (
                re.match(r'^مادة\s*\(\d+\)', trimmed) or
                re.match(r'^\[[A-Z]{2}\d{3}\]', trimmed) or
                re.match(r'^\d+\.\s+الأستاذ', trimmed) or
                re.match(r'^\[قاعة|^\[معمل', trimmed)
            )
            if is_header and current_lines:
                sec_text = "\n".join(current_lines).strip()
                if sec_text:
                    sec_id = f"{filename}#sec_{sec_counter}"
                    sections.append((sec_id, current_title, sec_text))
                    sec_counter += 1
                current_title = trimmed
                current_lines = [line]
            else:
                if is_header:
                    current_title = trimmed
                current_lines.append(line)

        if current_lines:
            sec_text = "\n".join(current_lines).strip()
            if sec_text:
                sec_id = f"{filename}#sec_{sec_counter}"
                sections.append((sec_id, current_title, sec_text))

        return sections

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the inverted index using TF-IDF & Cosine Similarity.
        Returns top-k matching documents ranked with score and highlighted snippet.
        """
        query_tokens = tokenize(query)
        if not query_tokens or self.total_docs == 0:
            return []

        # Query term frequencies
        q_tf: Dict[str, int] = {}
        for token in query_tokens:
            q_tf[token] = q_tf.get(token, 0) + 1

        # Query TF-IDF weights and query vector norm
        q_weights: Dict[str, float] = {}
        q_norm_sq = 0.0
        q_len = len(query_tokens)

        for term, count in q_tf.items():
            if term in self.idf:
                tf = count / q_len
                weight = tf * self.idf[term]
                q_weights[term] = weight
                q_norm_sq += weight * weight

        q_norm = math.sqrt(q_norm_sq)
        if q_norm == 0:
            return []

        # Find candidate documents containing at least one query term
        # and accumulate dot product: sum(w_q * w_d)
        scores: Dict[str, float] = {}
        for term, w_q in q_weights.items():
            if term in self.index:
                postings = self.index[term]
                idf = self.idf[term]
                for doc_id, count in postings.items():
                    doc = self.documents[doc_id]
                    w_d = (count / max(doc.length, 1)) * idf
                    scores[doc_id] = scores.get(doc_id, 0.0) + (w_q * w_d)

        # Calculate cosine similarity: dot_product / (norm_q * norm_d)
        ranked_results = []
        for doc_id, dot_product in scores.items():
            d_norm = self.doc_vector_norms.get(doc_id, 1.0)
            similarity = dot_product / (q_norm * d_norm)
            if similarity > 0.001:
                doc = self.documents[doc_id]
                ranked_results.append({
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "score": round(float(similarity), 4),
                    "source_file": doc.source_file,
                    "text": doc.text,
                    "snippet": self._extract_snippet(doc.text, query_tokens)
                })

        # Sort descending by cosine similarity score
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results[:top_k]

    def _extract_snippet(self, text: str, query_tokens: List[str], max_len: int = 250) -> str:
        """Extract a relevant snippet around the first matched token."""
        normalized_text = normalize_arabic(text.lower())
        best_pos = -1
        for token in query_tokens:
            pos = normalized_text.find(token)
            if pos != -1:
                best_pos = pos
                break

        if best_pos == -1:
            snippet = text[:max_len].replace("\n", " ").strip()
            return snippet + "..." if len(text) > max_len else snippet

        start = max(0, best_pos - 60)
        end = min(len(text), best_pos + max_len)
        snippet = text[start:end].replace("\n", " ").strip()
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{snippet}{suffix}"
