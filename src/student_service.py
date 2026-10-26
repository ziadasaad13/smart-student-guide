"""
Student Service
Encapsulates all student-facing capabilities:
- Profile management (passed courses, CGPA, level)
- Academic Information Retrieval using Inverted Index + TF-IDF + Cosine Similarity
- Knowledge Representation queries & Inference Engine (Eligibility, Prereqs, Standing)
- Query logging to queries.log
"""

from typing import Dict, List, Any, Optional
from src.file_manager import FileManager
from src.ir_engine import InvertedIndex
from src.knowledge_base import AcademicInferenceEngine, StudentProfile


class StudentService:
    def __init__(
        self,
        file_manager: FileManager,
        ir_index: InvertedIndex,
        inference_engine: AcademicInferenceEngine,
        current_student: Optional[StudentProfile] = None
    ):
        self.fm = file_manager
        self.ir_index = ir_index
        self.inference_engine = inference_engine
        self.student = current_student or StudentProfile(
            student_id="STD-202301",
            name="Zeyad",
            passed_courses=["MA112", "BC111", "MA113", "HU111", "MA114", "MA115", "MA116"],
            cgpa=3.4,
            completed_semesters=1,
            is_freshman_first_term=False
        )

    def set_student(self, student: StudentProfile):
        self.student = student
        # Persist student profile
        self.fm.save_student(student.to_dict())

    def load_student_by_id(self, student_id: str) -> Optional[StudentProfile]:
        students = self.fm.load_students()
        if student_id in students:
            std = StudentProfile.from_dict(students[student_id])
            self.student = std
            return std
        return None

    # ------------------------------------------------------------------
    # 1. Information Retrieval Search
    # ------------------------------------------------------------------
    def search_academic_information(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Searches bylaws, course descriptions, staff, and rooms using TF-IDF & Cosine Similarity."""
        results = self.ir_index.search(query, top_k=top_k)
        
        # Log this student query in data/queries.log
        top_titles = [r["title"] for r in results]
        summary = f"Found {len(results)} matches (Top: {top_titles[0] if top_titles else 'None'})"
        self.fm.log_query(
            user_role="student",
            query_category="information_retrieval",
            query_text=query,
            result_summary=summary
        )
        return results

    # ------------------------------------------------------------------
    # 2. Knowledge Representation & Inference Engine
    # ------------------------------------------------------------------
    def check_eligible_courses(self) -> Dict[str, Any]:
        """Inference engine answers: 'Which courses am I eligible to register for?'"""
        report = self.inference_engine.evaluate_course_eligibility(self.student)
        
        eligible_count = len(report["eligible_courses"])
        self.fm.log_query(
            user_role="student",
            query_category="inference_eligibility",
            query_text="Which courses am I eligible to register for?",
            result_summary=f"Inferred {eligible_count} eligible courses | Level: {report['academic_level']} | Standing: {report['academic_standing']}"
        )
        return report

    def check_specific_course(self, course_code: str) -> Dict[str, Any]:
        """Inference engine answers: 'Can I take course X?'"""
        result = self.inference_engine.can_register_course(self.student, course_code.strip().upper())
        status = "Eligible" if result.get("can_register") else "Ineligible"
        self.fm.log_query(
            user_role="student",
            query_category="inference_prerequisite_check",
            query_text=f"Can I register for {course_code}?",
            result_summary=f"{status} - {result.get('reason')}"
        )
        return result

    def get_prerequisite_path(self, course_code: str) -> Dict[str, Any]:
        """Explores prerequisite dependency chain."""
        tree = self.inference_engine.get_prerequisite_chain(course_code.strip().upper())
        self.fm.log_query(
            user_role="student",
            query_category="inference_prereq_chain",
            query_text=f"Prerequisite tree for {course_code}",
            result_summary=f"Traversed {len(tree.get('full_dependency_chain', []))} dependencies"
        )
        return tree

    # ------------------------------------------------------------------
    # 3. FAQ Browse
    # ------------------------------------------------------------------
    def get_faqs(self) -> List[Dict[str, Any]]:
        return self.fm.load_faqs()
