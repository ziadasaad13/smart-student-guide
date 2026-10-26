"""
Knowledge Representation (KR) and Inference Engine
- Models academic facts and bylaws rules (Kafrelsheikh AI Faculty)
- Forward-chaining inference for course eligibility ("Which courses am I eligible to register for?")
- Checks prerequisites, credit hour registration caps, academic standings, and graduation progress
"""

import json
from typing import Dict, List, Set, Optional, Any


class StudentProfile:
    def __init__(
        self,
        student_id: str = "STD-001",
        name: str = "Student",
        passed_courses: Optional[List[str]] = None,
        cgpa: float = 3.0,
        completed_semesters: int = 1,
        is_freshman_first_term: bool = False
    ):
        self.student_id = student_id
        self.name = name
        self.passed_courses: Set[str] = set(passed_courses or [])
        self.cgpa = float(cgpa)
        self.completed_semesters = int(completed_semesters)
        self.is_freshman_first_term = is_freshman_first_term

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "passed_courses": sorted(list(self.passed_courses)),
            "cgpa": self.cgpa,
            "completed_semesters": self.completed_semesters,
            "is_freshman_first_term": self.is_freshman_first_term
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProfile":
        return cls(
            student_id=data.get("student_id", "STD-001"),
            name=data.get("name", "Student"),
            passed_courses=data.get("passed_courses", []),
            cgpa=float(data.get("cgpa", 3.0)),
            completed_semesters=int(data.get("completed_semesters", 1)),
            is_freshman_first_term=bool(data.get("is_freshman_first_term", False))
        )


class AcademicInferenceEngine:
    def __init__(self, kb_path: str, courses_list: List[Dict[str, Any]]):
        self.kb_path = kb_path
        self.courses_by_code: Dict[str, Dict[str, Any]] = {
            c["course_code"]: c for c in courses_list
        }
        self.kb_data = self._load_kb(kb_path)
        self.prerequisites: Dict[str, List[str]] = self.kb_data.get("prerequisites", {})

    def _load_kb(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def reload(self, kb_path: str, courses_list: List[Dict[str, Any]]):
        self.kb_path = kb_path
        self.courses_by_code = {c["course_code"]: c for c in courses_list}
        self.kb_data = self._load_kb(kb_path)
        self.prerequisites = self.kb_data.get("prerequisites", {})

    # -------------------------------------------------------------
    # Rule 1: Calculate Passed Credit Hours
    # -------------------------------------------------------------
    def calculate_passed_hours(self, student: StudentProfile) -> int:
        total = 0
        for code in student.passed_courses:
            course = self.courses_by_code.get(code)
            if course:
                try:
                    total += int(course.get("credit_hours", 0))
                except (ValueError, TypeError):
                    pass
        return total

    # -------------------------------------------------------------
    # Rule 2: Determine Academic Level (Article 16)
    # -------------------------------------------------------------
    def determine_academic_level(self, passed_hours: int) -> Dict[str, Any]:
        if passed_hours < 30:
            return {"level_num": 1, "name": "Level 1 (Freshman - المستوى الأول)"}
        elif passed_hours < 65:
            return {"level_num": 2, "name": "Level 2 (Sophomore - المستوى الثاني)"}
        elif passed_hours < 100:
            return {"level_num": 3, "name": "Level 3 (Junior - المستوى الثالث)"}
        else:
            return {"level_num": 4, "name": "Level 4 (Senior - المستوى الرابع)"}

    # -------------------------------------------------------------
    # Rule 3: Determine Academic Standing & Probation (Article 22)
    # -------------------------------------------------------------
    def determine_academic_standing(self, student: StudentProfile) -> Dict[str, Any]:
        if student.is_freshman_first_term or student.completed_semesters <= 1:
            return {
                "standing": "Good Standing (حالة مستجدة)",
                "on_probation": False,
                "message": "طالب مستجد - لا يطبق الإنذار الأكاديمي في الفصل الأول."
            }
        
        if student.cgpa < 2.0:
            return {
                "standing": "Academic Probation (تحت الملاحظة الأكاديمية - إنذار أكاديمي)",
                "on_probation": True,
                "message": (
                    "تنبيه: معدلك التراكمي أقل من 2.00، أنت تحت الملاحظة الأكاديمية "
                    "وفقاً للمادة (22) من اللائحة. ينصح بإعادة مقررات لرفع المعدل وتجنب الفصل."
                )
            }
        else:
            return {
                "standing": "Good Standing (حالة أكاديمية جيدة)",
                "on_probation": False,
                "message": "المعدل التراكمي أعلى من أو يساوي 2.00، الوضع الأكاديمي سليم."
            }

    # -------------------------------------------------------------
    # Rule 4: Allowed Credit Hours Registration Cap (Article 8)
    # -------------------------------------------------------------
    def get_allowed_credit_limit(self, student: StudentProfile) -> Dict[str, Any]:
        min_hours = 9
        passed_hours = self.calculate_passed_hours(student)
        remaining_hours = max(0, 144 - passed_hours)

        # Special case: remaining hours less than 9 to graduate
        if remaining_hours < 9 and remaining_hours > 0:
            min_hours = remaining_hours

        if student.is_freshman_first_term:
            return {
                "min_hours": min_hours,
                "max_hours": 18,
                "rule_name": "Freshman First Semester",
                "notes": "الحد الأقصى للطلاب المستجدين هو 18 ساعة معتمدة."
            }

        # Senior graduating in this semester
        if remaining_hours <= 21 and passed_hours >= 123:
            return {
                "min_hours": min_hours,
                "max_hours": 21,
                "rule_name": "Graduation Semester",
                "notes": "فصل التخرج: يسمح بتسجيل حتى 21 ساعة معتمدة لاستكمال متطلبات التخرج."
            }

        cgpa = student.cgpa
        if cgpa >= 3.0:
            max_hours = 21
            notes = "معدل تراكمي ممتاز/جيد جداً (>= 3.00): يسمح بتسجيل حتى 21 ساعة معتمدة."
        elif cgpa >= 2.0:
            max_hours = 18
            notes = "معدل تراكمي عادي (من 2.00 حتى 2.99): الحد الأقصى 18 ساعة معتمدة."
        elif cgpa >= 1.0:
            max_hours = 15
            notes = "إنذار أكاديمي (من 1.00 حتى 1.99): الحد الأقصى مقيد بـ 15 ساعة معتمدة للمساعدة في رفع المعدل."
        else:
            max_hours = 12
            notes = "ملاحظة أكاديمية حرجة (أقل من 1.00): الحد الأقصى مقيد بـ 12 ساعة معتمدة فقط."

        return {
            "min_hours": min_hours,
            "max_hours": max_hours,
            "summer_max": 9,
            "rule_name": f"CGPA Band ({cgpa:.2f})",
            "notes": notes
        }

    # -------------------------------------------------------------
    # Rule 5: Forward Chaining Course Eligibility Engine
    # "Which courses am I eligible to register for?"
    # -------------------------------------------------------------
    def evaluate_course_eligibility(self, student: StudentProfile) -> Dict[str, Any]:
        passed_hours = self.calculate_passed_hours(student)
        level_info = self.determine_academic_level(passed_hours)
        standing_info = self.determine_academic_standing(student)
        credit_limits = self.get_allowed_credit_limit(student)

        eligible_courses = []
        locked_courses = []
        already_passed_courses = []

        for code, course in self.courses_by_code.items():
            title_ar = course.get("title_ar", "")
            title_en = course.get("title_en", "")
            credits = int(course.get("credit_hours", 3))
            c_level = int(course.get("level", 1))
            c_sem = int(course.get("semester", 1))

            if code in student.passed_courses:
                already_passed_courses.append({
                    "course_code": code,
                    "title_ar": title_ar,
                    "title_en": title_en,
                    "credit_hours": credits,
                    "level": c_level,
                    "semester": c_sem
                })
                continue

            # Check Prerequisites
            prereqs = self.prerequisites.get(code, [])
            missing_prereqs = []
            special_requirement_met = True
            special_reason = ""

            for p in prereqs:
                if p == "SPECIAL_100_HOURS":
                    if passed_hours < 100:
                        special_requirement_met = False
                        missing_prereqs.append(f"اجتياز 100 ساعة معتمدة (أنت أنجزت {passed_hours} ساعة فقط)")
                elif p not in student.passed_courses and p != "None" and p != "":
                    missing_prereqs.append(p)

            if not missing_prereqs and special_requirement_met:
                eligible_courses.append({
                    "course_code": code,
                    "title_ar": title_ar,
                    "title_en": title_en,
                    "credit_hours": credits,
                    "level": c_level,
                    "semester": c_sem,
                    "department": course.get("department", ""),
                    "course_type": course.get("course_type", "Core"),
                    "prerequisites_satisfied": prereqs
                })
            else:
                locked_courses.append({
                    "course_code": code,
                    "title_ar": title_ar,
                    "title_en": title_en,
                    "credit_hours": credits,
                    "level": c_level,
                    "semester": c_sem,
                    "missing_prerequisites": missing_prereqs
                })

        # Sort eligible courses by level and semester
        eligible_courses.sort(key=lambda x: (x["level"], x["semester"], x["course_code"]))
        locked_courses.sort(key=lambda x: (x["level"], x["semester"], x["course_code"]))

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "passed_hours": passed_hours,
            "remaining_hours": max(0, 144 - passed_hours),
            "academic_level": level_info["name"],
            "academic_standing": standing_info["standing"],
            "probation_alert": standing_info["message"],
            "credit_limits": credit_limits,
            "eligible_courses": eligible_courses,
            "locked_courses": locked_courses,
            "already_passed_courses": already_passed_courses
        }

    # -------------------------------------------------------------
    # Rule 6: Specific Course Eligibility Query ("Can I take course X?")
    # -------------------------------------------------------------
    def can_register_course(self, student: StudentProfile, course_code: str) -> Dict[str, Any]:
        course = self.courses_by_code.get(course_code)
        if not course:
            return {
                "can_register": False,
                "reason": f"المقرر {course_code} غير موجود في اللائحة الأكاديمية."
            }

        if course_code in student.passed_courses:
            return {
                "can_register": False,
                "reason": f"لقد اجتزت المقرر {course_code} ({course.get('title_ar')}) بالفعل بنجاح."
            }

        passed_hours = self.calculate_passed_hours(student)
        prereqs = self.prerequisites.get(course_code, [])
        missing = []

        for p in prereqs:
            if p == "SPECIAL_100_HOURS":
                if passed_hours < 100:
                    missing.append(f"اجتياز 100 ساعة معتمدة بنجاح (المجتاز حالياً: {passed_hours} ساعة)")
            elif p not in student.passed_courses and p != "None" and p != "":
                p_course = self.courses_by_code.get(p)
                p_name = p_course.get("title_ar") if p_course else p
                missing.append(f"{p} ({p_name})")

        if missing:
            return {
                "can_register": False,
                "course_code": course_code,
                "title_ar": course.get("title_ar"),
                "title_en": course.get("title_en"),
                "credit_hours": course.get("credit_hours"),
                "missing_prerequisites": missing,
                "reason": f"لا يمكنك تسجيل المقرر لعدم استيفاء المتطلبات السابقة: {', '.join(missing)}."
            }

        return {
            "can_register": True,
            "course_code": course_code,
            "title_ar": course.get("title_ar"),
            "title_en": course.get("title_en"),
            "credit_hours": course.get("credit_hours"),
            "satisfied_prerequisites": prereqs,
            "reason": f"نعم! أنت مؤهل لتسجيل مقرر {course_code} ({course.get('title_ar')}). جميع المتطلبات السابقة مكتملة."
        }

    # -------------------------------------------------------------
    # Rule 7: Prerequisite Chain / Dependency Path
    # -------------------------------------------------------------
    def get_prerequisite_chain(self, course_code: str) -> Dict[str, Any]:
        """Returns the full prerequisite dependency tree for a given course."""
        if course_code not in self.courses_by_code:
            return {"course": course_code, "error": "المقرر غير موجود"}

        chain = []
        visited = set()

        def dfs(code: str, depth: int):
            if code in visited or code == "SPECIAL_100_HOURS" or code == "None" or not code:
                return
            visited.add(code)
            prereqs = self.prerequisites.get(code, [])
            for p in prereqs:
                if p and p != "None":
                    dfs(p, depth + 1)
                    p_course = self.courses_by_code.get(p, {})
                    chain.append({
                        "course_code": p,
                        "title_ar": p_course.get("title_ar", ""),
                        "title_en": p_course.get("title_en", ""),
                        "is_direct_prereq_to": code,
                        "depth": depth + 1
                    })

        dfs(course_code, 0)
        target = self.courses_by_code[course_code]
        return {
            "target_course": course_code,
            "title_ar": target.get("title_ar", ""),
            "title_en": target.get("title_en", ""),
            "direct_prerequisites": self.prerequisites.get(course_code, []),
            "full_dependency_chain": chain
        }
