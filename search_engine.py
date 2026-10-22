"""Information Retrieval: tokenizer, inverted index, TF-IDF, cosine similarity.
Built from scratch (no sklearn) with light Arabic normalisation/stemming."""
import math
import re
from collections import Counter, defaultdict

_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")
_PREFIXES = ("وال", "بال", "كال", "فال", "لل", "ال")
_SUFFIXES = ("ات", "ان", "ون", "ين", "ها", "ه")


def normalize(text):
    text = text.lower().translate(_DIGITS)
    text = _DIACRITICS.sub("", text)
    text = re.sub("[إأآ]", "ا", text)
    return text.replace("ى", "ي").replace("ة", "ه")


_RAW_STOP = """the a an is are of to in and for on what how do does i my can me with or be by at it this that
في من على الى إلى عن هو هي ما ماذا هل كيف ان أن التي الذي هذا هذه و أو او يكون كان لا مع كل ده دا ايه إيه فين
امتى اي أي لو انا أنا عايز عاوز اعرف ممكن يعني بتاع بتاعة انت"""
STOPWORDS = {normalize(w) for w in _RAW_STOP.split()}


def light_stem(word):
    if re.match(r"[a-z]", word):                      # English: naive plural removal
        return word[:-1] if len(word) > 3 and word.endswith("s") and not word.endswith("ss") else word
    if re.match(r"[0-9]", word):
        return word
    for p in _PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 3:
            word = word[len(p):]
            break
    for s in _SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 3:
            return word[:-len(s)]
    return word


def tokenize(text):
    words = re.findall(r"[\u0621-\u064Aa-z0-9]+", normalize(text))
    return [light_stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


class SearchEngine:
    def __init__(self):
        self.docs = {}
        self.index = defaultdict(dict)     # term -> {doc_id: tf}
        self.idf = {}
        self.vectors = defaultdict(dict)   # doc_id -> {term: tf*idf}
        self.norms = {}

    def build(self, docs):
        """docs = {doc_id: text}"""
        self.docs = dict(docs)
        self.index = defaultdict(dict)
        self.vectors = defaultdict(dict)
        for doc_id, text in self.docs.items():
            for term, count in Counter(tokenize(text)).items():
                self.index[term][doc_id] = count
        n = len(self.docs)
        self.idf = {t: math.log(n / len(p)) + 1 for t, p in self.index.items()}
        for term, postings in self.index.items():
            for doc_id, tf in postings.items():
                self.vectors[doc_id][term] = tf * self.idf[term]
        self.norms = {d: math.sqrt(sum(x * x for x in v.values())) for d, v in self.vectors.items()}

    def search(self, query, top_k=5):
        q_vec = {t: tf * self.idf[t] for t, tf in Counter(tokenize(query)).items() if t in self.idf}
        if not q_vec:
            return []
        q_norm = math.sqrt(sum(x * x for x in q_vec.values()))
        dot = defaultdict(float)
        for term, qw in q_vec.items():
            for doc_id in self.index[term]:          # only docs containing the term are touched
                dot[doc_id] += qw * self.vectors[doc_id][term]
        results = [(d, s / (q_norm * self.norms[d])) for d, s in dot.items() if self.norms[d]]
        results.sort(key=lambda x: (-x[1], x[0]))
        return results[:top_k]

    def snippet(self, doc_id, query, width=220):
        """Return the line of the document that best matches the query."""
        q = set(tokenize(query))
        best, best_n = "", -1
        for line in self.docs.get(doc_id, "").splitlines()[1:]:
            n = len(q & set(tokenize(line)))
            if n > best_n and line.strip():
                best, best_n = line.strip(), n
        return best[:width] + ("..." if len(best) > width else "")

    def stats(self):
        return {"documents": len(self.docs), "terms": len(self.index)}
