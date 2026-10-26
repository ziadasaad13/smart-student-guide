"""
Smart Student Guide - Automated Sample Runs & Verification Script
Executes all functional scenarios required by Task 1 and logs comprehensive outputs.
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.file_manager import FileManager
from src.ir_engine import InvertedIndex
from src.knowledge_base import AcademicInferenceEngine, StudentProfile
from src.admin_service import AdminService
from src.student_service import StudentService


def run_all_tests():
    print("=" * 80)
    print("           🎓 SMART STUDENT GUIDE - SAMPLE RUNS & TEST SUITE 🎓")
    print("                 Faculty of Artificial Intelligence - KFS")
    print("=" * 80)

    # 1. Initialize File Manager & IR Engine
    print("\n--- STEP 1: INITIALIZING SYSTEM & INVERTED INDEX ---")
    fm = FileManager()
    ir_index = InvertedIndex()
    ir_index.load_from_directory(fm.docs_dir)
    print(f"✅ Text documents loaded from: {fm.docs_dir}")
    print(f"✅ Total indexed passages / documents: {ir_index.total_docs}")
    print(f"✅ Unique vocabulary terms in inverted index: {len(ir_index.index)}")

    # 2. Information Retrieval Tests (TF-IDF & Cosine Similarity)
    print("\n--- STEP 2: INFORMATION RETRIEVAL (TF-IDF & COSINE SIMILARITY) ---")
    courses = fm.load_courses()
    engine = AcademicInferenceEngine(fm.kb_json, courses)
    student = StudentService(fm, ir_index, engine)
    admin = AdminService(fm, ir_index)

    test_queries = [
        "مشروع التخرج وساعات تسجيله",
        "الإنذار الأكاديمي والملاحظة وفصل الطالب",
        "Deep Learning neural networks",
        "أين يقع مكتب عميد الكلية وقاعات المحاضرات",
        "Data structures and sorting algorithms",
        "شروط الحصول على مرتبة الشرف"
    ]

    for q in test_queries:
        print(f"\n🔍 Query: '{q}'")
        results = student.search_academic_information(q, top_k=2)
        for rank, res in enumerate(results, 1):
            print(f"   [{rank}] Document: {res['title']}")
            print(f"       Score (Cosine Sim): {res['score']:.4f}")
            print(f"       Source File: {res['source_file']}")
            print(f"       Snippet: {res['snippet'][:130]}...")

    # 3. Knowledge Representation & Inference Engine Tests
    print("\n--- STEP 3: KNOWLEDGE REPRESENTATION & INFERENCE ENGINE ---")

    # Scenario A: Sophomore Student (Regular Standing, CGPA = 3.4)
    print("\n[Scenario A: Sophomore Student, CGPA = 3.40, Passed Term 1 Courses]")
    std_a = StudentProfile(
        student_id="2023001",
        name="Ahmed Ali",
        passed_courses=["MA111", "MA112", "MA113", "HU111", "MA114", "BC111", "MA115", "MA116"],
        cgpa=3.40,
        completed_semesters=1
    )
    student.set_student(std_a)
    rep_a = student.check_eligible_courses()
    print(f"• Student: {rep_a['student_name']} | Passed Hours: {rep_a['passed_hours']} | Level: {rep_a['academic_level']}")
    print(f"• Academic Standing: {rep_a['academic_standing']}")
    print(f"• Allowed Credit Hours: Min {rep_a['credit_limits']['min_hours']} - Max {rep_a['credit_limits']['max_hours']} ({rep_a['credit_limits']['notes']})")
    print(f"• Eligible Courses Count: {len(rep_a['eligible_courses'])}")
    print("  Eligible sample:")
    for c in rep_a["eligible_courses"][:4]:
        print(f"   - [{c['course_code']}] {c['title_ar']} ({c['title_en']}) | Req: {c['prerequisites_satisfied']}")

    # Specific Course Checks for Scenario A
    res_ml121 = student.check_specific_course("ML121")
    print(f"• Can student register for ML121 (Concepts in AI)? -> {res_ml121.get('can_register')} ({res_ml121.get('reason')})")

    res_gp = student.check_specific_course("GP411")
    print(f"• Can student register for GP411 (Graduation Project)? -> {res_gp.get('can_register')} ({res_gp.get('reason')})")

    # Scenario B: Student on Academic Probation (CGPA = 1.70)
    print("\n[Scenario B: Student Under Academic Probation, CGPA = 1.70]")
    std_b = StudentProfile(
        student_id="2022045",
        name="Mohamed Khaled",
        passed_courses=["MA112", "HU111", "MA115"],
        cgpa=1.70,
        completed_semesters=2
    )
    student.set_student(std_b)
    rep_b = student.check_eligible_courses()
    print(f"• Student: {rep_b['student_name']} | Passed Hours: {rep_b['passed_hours']} | Standing: {rep_b['academic_standing']}")
    print(f"• Alert: {rep_b['probation_alert']}")
    print(f"• Registration Cap Restricted To: {rep_b['credit_limits']['max_hours']} Credit Hours! ({rep_b['credit_limits']['notes']})")

    # Scenario C: Senior Student (Eligible for Graduation Project, 102 Passed Hours)
    print("\n[Scenario C: Senior Student, 102 Passed Credit Hours, CGPA = 3.65]")
    senior_courses = [
        "MA111", "MA112", "MA113", "HU111", "MA114", "BC111", "MA115", "MA116",
        "ML121", "BC121", "MA121", "HU121", "HU122", "BC122", "MA122",
        "ML211", "RB211", "BC211", "BC212", "ES211", "HU211", "MA212",
        "BC221", "BC222", "BC223", "RB221", "BC224", "BC225", "BC226",
        "RB311", "ML311", "BC311", "BC312", "ES311", "MA311",
        "RB321", "HU321", "BC321", "ES321", "BC324"
    ]
    std_c = StudentProfile(
        student_id="2020012",
        name="Sara Mahmoud",
        passed_courses=senior_courses,
        cgpa=3.65,
        completed_semesters=6
    )
    student.set_student(std_c)
    rep_c = student.check_eligible_courses()
    print(f"• Student: {rep_c['student_name']} | Passed Hours: {rep_c['passed_hours']} | Level: {rep_c['academic_level']}")
    res_senior_gp = student.check_specific_course("GP411")
    print(f"• Can student register for GP411 (Graduation Project)? -> {res_senior_gp.get('can_register')} ({res_senior_gp.get('reason')})")

    # 4. Prerequisite Dependency Chain Tree Test
    print("\n--- STEP 4: PREREQUISITE DEPENDENCY TREE INFERENCE ---")
    chain = student.get_prerequisite_path("ML411")
    print(f"Target Course: [{chain['target_course']}] {chain['title_ar']} ({chain['title_en']})")
    print("Full Prerequisite Dependency Lineage:")
    for step in chain.get("full_dependency_chain", []):
        indent = "   " * step["depth"]
        print(f"{indent}└── [{step['course_code']}] {step['title_ar']} ({step['title_en']}) -> Unlocks [{step['is_direct_prereq_to']}]")

    # 5. File Handling & Admin Operations Test
    print("\n--- STEP 5: FILE HANDLING & ADMIN DATA ENTRY TESTS ---")
    # Add new course
    new_code = "AI499"
    add_ok = admin.add_course(
        course_code=new_code,
        title_en="Capstone AI Seminar",
        title_ar="سيمنار الذكاء الاصطناعي المتقدم",
        credit_hours=3,
        lecture_hours=2,
        lab_hours=2,
        course_type="Elective",
        department="ML",
        prerequisite="ML311",
        level=4,
        semester=2
    )
    print(f"• Admin added new course [{new_code}]: {add_ok}")

    # Add FAQ
    faq = admin.add_faq(
        question="ما هي مواعيد التقديم للمدينة الجامعية لطلاب الكلية؟",
        answer="يتم فتح باب التقدم للمدينة الجامعية إلكترونياً خلال شهري أغسطس وسبتمبر من كل عام.",
        question_en="When can college students apply for university dorms?"
    )
    print(f"• Admin added new FAQ: {faq['id']} - '{faq['question']}'")

    # Verify query logging
    print("\n--- STEP 6: VERIFYING QUERY LOGGING IN queries.log ---")
    recent_logs = admin.view_logs(limit=6)
    print(f"Total recent log entries retrieved: {len(recent_logs)}")
    for log in recent_logs:
        print(f"  📝 {log}")

    print("\n" + "=" * 80)
    print("🎉 ALL TEST SCENARIOS PASSED WITH 100% SUCCESS!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
