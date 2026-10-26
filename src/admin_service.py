"""
Admin Service
Encapsulates all administrative features:
- Add / edit courses in CSV and sync with Knowledge Base
- Add / edit text documents in documents/ and trigger IR Inverted Index re-indexing
- Add / edit FAQs in JSON
- View system statistics and recent query logs
"""

from typing import Dict, List, Any
from src.file_manager import FileManager
from src.ir_engine import InvertedIndex


class AdminService:
    def __init__(self, file_manager: FileManager, ir_index: InvertedIndex):
        self.fm = file_manager
        self.ir_index = ir_index

    def get_stats(self) -> Dict[str, Any]:
        courses = self.fm.load_courses()
        docs = self.fm.list_documents()
        faqs = self.fm.load_faqs()
        staff = self.fm.load_staff()
        rooms = self.fm.load_rooms()
        logs = self.fm.get_recent_logs(100)
        return {
            "total_courses": len(courses),
            "total_documents": len(docs),
            "indexed_passages": self.ir_index.total_docs,
            "total_faqs": len(faqs),
            "total_staff": len(staff),
            "total_rooms": len(rooms),
            "logged_queries_count": len(logs)
        }

    # -------------------------------------------------------------
    # Course Management
    # -------------------------------------------------------------
    def list_courses(self) -> List[Dict[str, Any]]:
        return self.fm.load_courses()

    def add_course(
        self,
        course_code: str,
        title_en: str,
        title_ar: str,
        credit_hours: int,
        lecture_hours: int,
        lab_hours: int,
        course_type: str,
        department: str,
        prerequisite: str,
        level: int,
        semester: int
    ) -> bool:
        course_data = {
            "course_code": course_code.strip().upper(),
            "title_en": title_en.strip(),
            "title_ar": title_ar.strip(),
            "credit_hours": str(credit_hours),
            "lecture_hours": str(lecture_hours),
            "lab_hours": str(lab_hours),
            "course_type": course_type.strip(),
            "department": department.strip().upper(),
            "prerequisite": prerequisite.strip().upper() if prerequisite else "None",
            "level": str(level),
            "semester": str(semester)
        }
        success = self.fm.add_course(course_data)
        if success:
            self.fm.log_query(
                user_role="admin",
                query_category="admin_action",
                query_text=f"Add Course {course_code}",
                result_summary=f"Successfully added course {course_code} ({title_ar})"
            )
        return success

    def update_course(self, course_code: str, updated_fields: Dict[str, Any]) -> bool:
        success = self.fm.update_course(course_code, updated_fields)
        if success:
            self.fm.log_query(
                user_role="admin",
                query_category="admin_action",
                query_text=f"Update Course {course_code}",
                result_summary=f"Successfully updated fields: {list(updated_fields.keys())}"
            )
        return success

    # -------------------------------------------------------------
    # Document Management & Inverted Index Refresh
    # -------------------------------------------------------------
    def list_documents(self) -> List[str]:
        return self.fm.list_documents()

    def read_document(self, filename: str) -> str:
        return self.fm.read_document(filename)

    def save_document(self, filename: str, content: str) -> str:
        saved_path = self.fm.save_document(filename, content)
        # Re-build Inverted Index automatically
        self.ir_index.load_from_directory(self.fm.docs_dir)
        self.fm.log_query(
            user_role="admin",
            query_category="admin_action",
            query_text=f"Save Document {filename}",
            result_summary=f"Saved document and re-indexed {self.ir_index.total_docs} passages"
        )
        return saved_path

    # -------------------------------------------------------------
    # FAQ Management
    # -------------------------------------------------------------
    def list_faqs(self) -> List[Dict[str, Any]]:
        return self.fm.load_faqs()

    def add_faq(self, question: str, answer: str, question_en: str = "") -> Dict[str, Any]:
        new_faq = self.fm.add_faq(question, answer, question_en)
        self.fm.log_query(
            user_role="admin",
            query_category="admin_action",
            query_text=f"Add FAQ: {question[:40]}...",
            result_summary=f"Created FAQ {new_faq['id']}"
        )
        return new_faq

    # -------------------------------------------------------------
    # Log Inspection
    # -------------------------------------------------------------
    def view_logs(self, limit: int = 20) -> List[str]:
        return self.fm.get_recent_logs(limit)
