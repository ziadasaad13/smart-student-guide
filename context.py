"""Holds all loaded data + the search engines + the knowledge base. reload() after any admin change."""
import config
import file_manager as fm
from knowledge_base import KnowledgeBase
from search_engine import SearchEngine


class Context:
    def __init__(self):
        self.reload()

    def reload(self):
        self.courses = fm.load_courses()
        self.rules = fm.load_rules()
        self.kb = KnowledgeBase(self.courses, self.rules)
        self.staff = fm.load_staff()
        self.schedule = fm.load_schedule()
        self.faqs = fm.load_faqs()
        self.docs = fm.load_documents()
        self.doc_engine = SearchEngine()
        self.doc_engine.build(self.docs)
        self.faq_engine = SearchEngine()
        self.faq_engine.build({str(i): f"{f['q']} {f.get('keywords', '')}" for i, f in enumerate(self.faqs)})

    def doc_title(self, doc_id):
        text = self.docs.get(doc_id, "")
        return text.splitlines()[0] if text else doc_id

    def answer_question(self, question):
        """FAQ first (high confidence) -> otherwise top documents. Returns a dict."""
        faq_hits = self.faq_engine.search(question, 1)
        if faq_hits and faq_hits[0][1] >= config.FAQ_THRESHOLD:
            i, score = faq_hits[0]
            f = self.faqs[int(i)]
            return {"type": "faq", "score": score, "question": f["q"], "answer": f["a"], "source": f.get("source", "")}
        hits = self.doc_engine.search(question, config.TOP_K_DOCS)
        return {"type": "docs", "results": [
            {"doc": d, "title": self.doc_title(d), "score": s, "snippet": self.doc_engine.snippet(d, question)}
            for d, s in hits]}
