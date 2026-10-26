"""
File Handling Manager
- Reads and stores data in TXT, CSV, and JSON formats
- Records all user and student queries with timestamps in queries.log
- Manages courses, documents, staff, rooms, FAQs, and knowledge base files
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class FileManager:
    def __init__(self, base_data_dir: Optional[str] = None):
        if base_data_dir is None:
            # Dynamically detect project root / data directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_dir = os.path.join(project_root, "data")
        else:
            self.base_dir = base_data_dir
        self.docs_dir = os.path.join(self.base_dir, "documents")
        self.courses_csv = os.path.join(self.base_dir, "courses.csv")
        self.staff_csv = os.path.join(self.base_dir, "staff.csv")
        self.rooms_csv = os.path.join(self.base_dir, "rooms.csv")
        self.kb_json = os.path.join(self.base_dir, "knowledge_base.json")
        self.faqs_json = os.path.join(self.base_dir, "faqs.json")
        self.log_file = os.path.join(self.base_dir, "queries.log")
        self.students_json = os.path.join(self.base_dir, "students.json")

        # Ensure directories exist
        os.makedirs(self.docs_dir, exist_ok=True)
        # Ensure log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"# Smart Student Guide - Query Log Started {datetime.now().isoformat()}\n")

    # ------------------------------------------------------------------
    # TXT Document Handling
    # ------------------------------------------------------------------
    def list_documents(self) -> List[str]:
        """List all .txt documents in the documents folder."""
        if not os.path.exists(self.docs_dir):
            return []
        return sorted([f for f in os.listdir(self.docs_dir) if f.endswith(".txt")])

    def read_document(self, filename: str) -> str:
        """Read full text of a specific .txt document."""
        filepath = os.path.join(self.docs_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def save_document(self, filename: str, content: str) -> str:
        """Create or update a .txt document."""
        if not filename.endswith(".txt"):
            filename += ".txt"
        filepath = os.path.join(self.docs_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    # ------------------------------------------------------------------
    # CSV Handling: Courses
    # ------------------------------------------------------------------
    def load_courses(self) -> List[Dict[str, Any]]:
        """Loads courses from courses.csv."""
        if not os.path.exists(self.courses_csv):
            return []
        courses = []
        with open(self.courses_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                courses.append(dict(row))
        return courses

    def save_courses(self, courses: List[Dict[str, Any]]):
        """Saves courses back to courses.csv."""
        if not courses:
            return
        fieldnames = list(courses[0].keys())
        with open(self.courses_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(courses)

    def add_course(self, course_data: Dict[str, Any]) -> bool:
        """Adds a new course and updates the knowledge base prerequisites."""
        courses = self.load_courses()
        code = course_data.get("course_code", "").strip().upper()
        if not code:
            return False
        
        # Check if exists
        for c in courses:
            if c.get("course_code") == code:
                return False  # already exists

        courses.append(course_data)
        self.save_courses(courses)

        # Update KB prerequisites
        kb = self.load_knowledge_base()
        prereq = course_data.get("prerequisite", "None")
        if "prerequisites" not in kb:
            kb["prerequisites"] = {}
        if prereq and prereq != "None":
            kb["prerequisites"][code] = [prereq]
        else:
            kb["prerequisites"][code] = []
        self.save_knowledge_base(kb)
        return True

    def update_course(self, course_code: str, updated_fields: Dict[str, Any]) -> bool:
        """Updates fields of an existing course."""
        courses = self.load_courses()
        found = False
        for c in courses:
            if c.get("course_code") == course_code:
                c.update(updated_fields)
                found = True
                break
        if found:
            self.save_courses(courses)
            if "prerequisite" in updated_fields:
                kb = self.load_knowledge_base()
                prereq = updated_fields["prerequisite"]
                if prereq and prereq != "None":
                    kb["prerequisites"][course_code] = [prereq]
                else:
                    kb["prerequisites"][course_code] = []
                self.save_knowledge_base(kb)
        return found

    # ------------------------------------------------------------------
    # CSV Handling: Staff and Rooms
    # ------------------------------------------------------------------
    def load_staff(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.staff_csv):
            return []
        with open(self.staff_csv, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def load_rooms(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.rooms_csv):
            return []
        with open(self.rooms_csv, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ------------------------------------------------------------------
    # JSON Handling: Knowledge Base & FAQs
    # ------------------------------------------------------------------
    def load_knowledge_base(self) -> Dict[str, Any]:
        if not os.path.exists(self.kb_json):
            return {}
        with open(self.kb_json, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_knowledge_base(self, kb_data: Dict[str, Any]):
        with open(self.kb_json, "w", encoding="utf-8") as f:
            json.dump(kb_data, f, ensure_ascii=False, indent=2)

    def load_faqs(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.faqs_json):
            return []
        with open(self.faqs_json, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_faqs(self, faqs: List[Dict[str, Any]]):
        with open(self.faqs_json, "w", encoding="utf-8") as f:
            json.dump(faqs, f, ensure_ascii=False, indent=2)

    def add_faq(self, question: str, answer: str, question_en: str = "") -> Dict[str, Any]:
        faqs = self.load_faqs()
        new_id = f"faq_{len(faqs) + 1:02d}"
        new_faq = {
            "id": new_id,
            "question": question,
            "question_en": question_en or question,
            "answer": answer
        }
        faqs.append(new_faq)
        self.save_faqs(faqs)
        return new_faq

    # ------------------------------------------------------------------
    # JSON Handling: Student Profiles
    # ------------------------------------------------------------------
    def load_students(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.students_json):
            return {}
        try:
            with open(self.students_json, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_student(self, student_dict: Dict[str, Any]):
        students = self.load_students()
        std_id = student_dict.get("student_id", "STD-001")
        students[std_id] = student_dict
        with open(self.students_json, "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Query Logging (Log file handling requirement)
    # ------------------------------------------------------------------
    def log_query(self, user_role: str, query_category: str, query_text: str, result_summary: str):
        """
        Records user query in data/queries.log with ISO timestamp.
        Formats:
        [YYYY-MM-DD HH:MM:SS] [ROLE] [CATEGORY] Query: <text> | Result: <summary>
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [USER: {user_role.upper()}] [TYPE: {query_category.upper()}] Query: \"{query_text}\" | Outcome: {result_summary}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def get_recent_logs(self, limit: int = 15) -> List[str]:
        """Retrieve recent query log entries."""
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return lines[-limit:]
