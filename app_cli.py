"""
Smart Student Guide - Interactive CLI Application
Terminal user interface supporting Admin and Student workflows.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.file_manager import FileManager
from src.ir_engine import InvertedIndex
from src.knowledge_base import AcademicInferenceEngine, StudentProfile
from src.admin_service import AdminService
from src.student_service import StudentService


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 72)
    print("       🎓 SMART STUDENT GUIDE - دليل الطالب الذكي 🎓")
    print("    كلية الذكاء الاصطناعي - جامعة كفر الشيخ (برنامج عام 2023)")
    print("                   ❤️  فريق العمل: قصة عشق  ❤️")
    print("=" * 72)


class SmartStudentApp:
    def __init__(self):
        self.fm = FileManager()
        self.ir_index = InvertedIndex()
        print("⏳ جاري تحميل وفهرسة الوثائق الأكاديمية وبناء Inverted Index...")
        self.ir_index.load_from_directory(self.fm.docs_dir)
        
        courses = self.fm.load_courses()
        self.inference_engine = AcademicInferenceEngine(self.fm.kb_json, courses)
        
        # Default sample student
        default_student = StudentProfile(
            student_id="2023001",
            name="Zeyad",
            passed_courses=["MA112", "BC111", "MA113", "HU111", "MA114", "MA115", "MA116"],
            cgpa=3.40,
            completed_semesters=1,
            is_freshman_first_term=False
        )
        self.student_service = StudentService(self.fm, self.ir_index, self.inference_engine, default_student)
        self.admin_service = AdminService(self.fm, self.ir_index)

    def main_menu(self):
        while True:
            print_banner()
            print("1. 👤 Student Interface (واجهة الطالب - استعلامات واستدلال أكاديمي)")
            print("2. 🛠️  Admin Interface (واجهة الإدارة - إضافة مقررات ووثائق ولوائح)")
            print("3. ⚡ Run Quick Automated Demo (تشغيل تجريبي فوري شامل)")
            print("4. 🚪 Exit (خروج)")
            print("-" * 72)
            choice = input("👉 اختر رقم القائمة [1-4]: ").strip()

            if choice == "1":
                self.student_menu()
            elif choice == "2":
                self.admin_menu()
            elif choice == "3":
                self.run_demo()
            elif choice == "4":
                print("\nشكراً لاستخدامك نظام دليل الطالب الذكي. مع أطيب التمنيات بالتوفيق! 🌟\n")
                break
            else:
                input("\n⚠️ اختيار غير صالح. اضغط Enter للمحاولة مرة أخرى...")

    # ==================================================================
    # STUDENT WORKFLOW
    # ==================================================================
    def student_menu(self):
        while True:
            std = self.student_service.student
            passed_hrs = self.inference_engine.calculate_passed_hours(std)
            lvl = self.inference_engine.determine_academic_level(passed_hrs)["name"]

            print("\n" + "=" * 72)
            print(f"👤 واجهة الطالب | الطالب: {std.name} ({std.student_id})")
            print(f"📊 المستوى: {lvl} | الساعات المنجزة: {passed_hrs} | المعدل: {std.cgpa:.2f}")
            print("=" * 72)
            print("1. 🔍 البحث في لوائح الكلية والمقررات والقاعات والدكاترة (IR + TF-IDF)")
            print("2. 📋 الاستدلال الأكاديمي: ما هي المقررات المؤهل لتسجيلها؟ (Inference Engine)")
            print("3. ❓ التحقق من مقرر محدد: هل يمكنني تسجيل المقرر X؟")
            print("4. 🌳 عرض شجرة المتطلبات السابقة لمقرر (Prerequisite Dependency Chain)")
            print("5. ✏️  تعديل بيانات الطالب والمقررات المجتازة")
            print("6. 💡 استعراض الأسئلة الشائعة للكلية (FAQs)")
            print("7. ⬅️  العودة للقائمة الرئيسية")
            print("-" * 72)

            ch = input("👉 اختر العملية [1-7]: ").strip()
            if ch == "1":
                self.handle_ir_search()
            elif ch == "2":
                self.handle_eligibility_check()
            elif ch == "3":
                self.handle_single_course_check()
            elif ch == "4":
                self.handle_prereq_chain()
            elif ch == "5":
                self.handle_update_student_profile()
            elif ch == "6":
                self.handle_browse_faqs()
            elif ch == "7":
                break

    def handle_ir_search(self):
        print("\n--- 🔍 محرك استرجاع المعلومات (Information Retrieval Engine) ---")
        print("يمكنك البحث باللغة العربية أو الإنجليزية عن أي موضوع، مثل:")
        print("  - مشروع التخرج | الإنذار الأكاديمي | شروط مرتبة الشرف | الساعات المعتمدة")
        print("  - Deep Learning | Natural Language Processing | مكتب العميد | معمل الروبوتات")
        q = input("\n🔎 اكتب استفسارك الأكاديمي: ").strip()
        if not q:
            return

        results = self.student_service.search_academic_information(q, top_k=4)
        print(f"\n📑 نتائج البحث لـ: '{q}' (مرتبة حسب Cosine Similarity):")
        print("=" * 72)
        if not results:
            print("❌ لم يتم العثور على وثائق مطابقة لاستفسارك.")
        else:
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['title']}  |  (Similarity Score: {r['score']:.4f})")
                print(f"    المصدر: {r['source_file']}")
                print(f"    مقتطف: {r['snippet']}")
                print("-" * 72)
        input("\nاضغط Enter للمتابعة...")

    def handle_eligibility_check(self):
        print("\n--- 📋 محرك الاستدلال وقاعدة المعرفة (Inference Engine) ---")
        rep = self.student_service.check_eligible_courses()

        print("\n📌 تقرير الحالة الأكاديمية والتسجيل:")
        print(f" • الطالب: {rep['student_name']} ({rep['student_id']})")
        print(f" • المستوى الدراسي: {rep['academic_level']}")
        print(f" • الساعات المعتمدة المجتازة: {rep['passed_hours']} ساعة (المتبقي للتخرج: {rep['remaining_hours']} ساعة)")
        print(f" • الحالة الأكاديمية: {rep['academic_standing']}")
        print(f" • التنبيه الأكاديمي: {rep['probation_alert']}")
        print(f" • حدود ساعات التسجيل للفصل القادم:")
        print(f"    - الحد الأدنى: {rep['credit_limits']['min_hours']} ساعات")
        print(f"    - الحد الأقصى: {rep['credit_limits']['max_hours']} ساعة ({rep['credit_limits']['notes']})")

        print("\n✅ المقررات المتاح لك تسجيلها الآن (استوفت متطلباتها):")
        print("-" * 72)
        eligible = rep["eligible_courses"]
        if not eligible:
            print("لا توجد مقررات متاحة حالياً.")
        else:
            for c in eligible:
                p_text = ", ".join(c["prerequisites_satisfied"]) if c["prerequisites_satisfied"] else "بدون متطلب"
                print(f" • [{c['course_code']}] {c['title_ar']} ({c['title_en']}) | ساعات: {c['credit_hours']} | المستوى: {c['level']} | المتطلب: {p_text}")

        print(f"\n🔒 مقررات لا يمكنك تسجيلها لعدم استيفاء المتطلبات ({len(rep['locked_courses'])} مقرر):")
        for c in rep["locked_courses"][:6]:
            print(f" • [{c['course_code']}] {c['title_ar']} ⬅️ يتطلب: {', '.join(c['missing_prerequisites'])}")
        if len(rep["locked_courses"]) > 6:
            print(f"   ... و {len(rep['locked_courses']) - 6} مقررات أخرى مقفلة.")

        input("\nاضغط Enter للمتابعة...")

    def handle_single_course_check(self):
        print("\n--- ❓ فحص أهلية التسجيل لمقرر محدد ---")
        code = input("اكتب كود المقرر (مثال: ML211, BC223, GP411, ES411): ").strip().upper()
        if not code:
            return
        res = self.student_service.check_specific_course(code)
        print("\nنتيجة الفحص:")
        print("=" * 60)
        if res.get("can_register"):
            print(f"✅ مبروك! مؤهل للتسجيل في: {res.get('course_code')} - {res.get('title_ar')}")
            print(f"   {res.get('reason')}")
        else:
            print(f"❌ غير مؤهل للتسجيل في: {code}")
            print(f"   السبب: {res.get('reason')}")
        print("=" * 60)
        input("\nاضغط Enter للمتابعة...")

    def handle_prereq_chain(self):
        print("\n--- 🌳 مسار المتطلبات السابقة للمقرر (Dependency Chain) ---")
        code = input("اكتب كود المقرر لتتبع شجرة متطلباته (مثال: ML311, BC312, GP421, ES421): ").strip().upper()
        if not code:
            return
        tree = self.student_service.get_prerequisite_path(code)
        if "error" in tree:
            print(f"❌ {tree['error']}")
        else:
            print(f"\nالمقرر المستهدف: [{tree['target_course']}] {tree['title_ar']} ({tree['title_en']})")
            chain = tree["full_dependency_chain"]
            if not chain:
                print(" • هذا المقرر لا يعتمد على أي متطلبات سابقة (مقرر مستوى أول أو حر).")
            else:
                print(" • مسار المتطلبات التراكمية من البداية إلى الهدف:")
                for step in chain:
                    indent = "    " * (step["depth"] - 1)
                    print(f"{indent}└── [{step['course_code']}] {step['title_ar']} ({step['title_en']}) ➡️ يفتح [{step['is_direct_prereq_to']}]")
        input("\nاضغط Enter للمتابعة...")

    def handle_update_student_profile(self):
        print("\n--- ✏️ تعديل بيانات الطالب الحالية ---")
        std = self.student_service.student
        print(f"الاسم الحالي: {std.name} | الرقم الجامعي: {std.student_id}")
        print(f"المواد المجتازة حالياً ({len(std.passed_courses)}): {', '.join(sorted(std.passed_courses))}")
        print(f"المعدل التراكمي CGPA: {std.cgpa}")

        new_name = input(f"الاسم الجديد (Enter للإبقاء على '{std.name}'): ").strip() or std.name
        new_gpa_str = input(f"المعدل التراكمي CGPA الجديد [0.0 - 4.0] (Enter للإبقاء على {std.cgpa}): ").strip()
        new_gpa = float(new_gpa_str) if new_gpa_str else std.cgpa

        print("\nالمواد المجتازة: أدخل أكواد المواد مفصولة بفواصل (أو Enter للإبقاء عليها)")
        print("أمثلة: MA111, MA112, BC111, ML121, BC121, ML211, BC211")
        new_courses_input = input("أكواد المقررات: ").strip()
        if new_courses_input:
            new_courses = [c.strip().upper() for c in new_courses_input.split(",") if c.strip()]
        else:
            new_courses = list(std.passed_courses)

        updated_student = StudentProfile(
            student_id=std.student_id,
            name=new_name,
            passed_courses=new_courses,
            cgpa=new_gpa,
            completed_semesters=std.completed_semesters,
            is_freshman_first_term=False
        )
        self.student_service.set_student(updated_student)
        print("✅ تم حفظ وتحديث بيانات الطالب بنجاح!")
        input("\nاضغط Enter للمتابعة...")

    def handle_browse_faqs(self):
        print("\n--- 💡 الأسئلة الشائعة (Frequently Asked Questions) ---")
        faqs = self.student_service.get_faqs()
        for i, faq in enumerate(faqs, 1):
            print(f"\n[{i}] س: {faq['question']}")
            print(f"    ج: {faq['answer']}")
            print("-" * 60)
        input("\nاضغط Enter للمتابعة...")

    # ==================================================================
    # ADMIN WORKFLOW
    # ==================================================================
    def admin_menu(self):
        while True:
            stats = self.admin_service.get_stats()
            print("\n" + "=" * 72)
            print("🛠️  واجهة الإدارة الأكاديمية (Academic Administrator)")
            print(f"📊 المقررات: {stats['total_courses']} | الوثائق: {stats['total_documents']} | المقاطع المفهرسة: {stats['indexed_passages']} | الأسئلة: {stats['total_faqs']}")
            print("=" * 72)
            print("1. 📚 استعراض جميع المقررات في النظام (CSV)")
            print("2. ➕ إضافة مقرر دراسي جديد (Updates CSV & Knowledge Base)")
            print("3. 📝 إضافة وثيقة لائحة جديدة أو تعديل نص (Re-indexes IR Inverted Index)")
            print("4. ❓ إضافة سؤال شائع جديد (JSON FAQ)")
            print("5. 📋 استعراض سجل استعلامات الطلاب والعمليات (Query Log File)")
            print("6. ⬅️  العودة للقائمة الرئيسية")
            print("-" * 72)

            ch = input("👉 اختر العملية [1-6]: ").strip()
            if ch == "1":
                courses = self.admin_service.list_courses()
                print("\nقائمة المقررات المسجلة في النظام:")
                print(f"{'الكود':<8} | {'اسم المقرر بالعربية':<32} | {'ساعات':<5} | {'المتطلب السابق':<12}")
                print("-" * 65)
                for c in courses:
                    print(f"{c['course_code']:<8} | {c['title_ar']:<32} | {c['credit_hours']:<5} | {c.get('prerequisite', 'None'):<12}")
                input("\nاضغط Enter للمتابعة...")
            elif ch == "2":
                self.handle_admin_add_course()
            elif ch == "3":
                self.handle_admin_add_document()
            elif ch == "4":
                self.handle_admin_add_faq()
            elif ch == "5":
                logs = self.admin_service.view_logs(20)
                print("\n📋 أحدث السجلات من queries.log:")
                print("=" * 72)
                for line in logs:
                    print(line)
                print("=" * 72)
                input("\nاضغط Enter للمتابعة...")
            elif ch == "6":
                break

    def handle_admin_add_course(self):
        print("\n--- ➕ إضافة مقرر دراسي جديد ---")
        code = input("كود المقرر (مثال: AI499): ").strip().upper()
        if not code:
            return
        title_ar = input("اسم المقرر بالعربية: ").strip()
        title_en = input("اسم المقرر بالإنجليزية: ").strip()
        credits = int(input("عدد الساعات المعتمدة (مثال: 3): ").strip() or "3")
        lect = int(input("ساعات المحاضرة: ").strip() or "2")
        lab = int(input("ساعات العملي/التمارين: ").strip() or "2")
        c_type = input("نوع المقرر (Core / Elective): ").strip() or "Core"
        dept = input("القسم (ML, RB, ES, BC, HU, MA): ").strip().upper() or "ML"
        prereq = input("المتطلب السابق (كود المقرر أو None): ").strip().upper() or "None"
        lvl = int(input("المستوى (1-4): ").strip() or "4")
        sem = int(input("الفصل (1 أو 2): ").strip() or "1")

        success = self.admin_service.add_course(
            course_code=code,
            title_en=title_en,
            title_ar=title_ar,
            credit_hours=credits,
            lecture_hours=lect,
            lab_hours=lab,
            course_type=c_type,
            department=dept,
            prerequisite=prereq,
            level=lvl,
            semester=sem
        )
        if success:
            print(f"✅ تم إضافة المقرر [{code}] {title_ar} بنجاح إلى ملف CSV وقاعدة المعرفة!")
        else:
            print(f"❌ فشل الإضافة: قد يكون المقرر [{code}] موجود بالفعل.")
        input("\nاضغط Enter للمتابعة...")

    def handle_admin_add_document(self):
        print("\n--- 📝 إضافة / تحديث وثيقة لائحة ---")
        fname = input("اسم الملف (مثال: student_activities.txt): ").strip()
        if not fname:
            return
        print("اكتب محتوى الوثيقة (اضغط Enter بعد الانتهاء، ثم اكتب END في سطر منفصل):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        content = "\n".join(lines).strip()
        if content:
            path = self.admin_service.save_document(fname, content)
            print(f"✅ تم حفظ الوثيقة في {path} وإعادة بناء الـ Inverted Index بنجاح!")
        input("\nاضغط Enter للمتابعة...")

    def handle_admin_add_faq(self):
        print("\n--- ❓ إضافة سؤال شائع جديد ---")
        q = input("نص السؤال بالعربية: ").strip()
        if not q:
            return
        q_en = input("نص السؤال بالإنجليزية (اختياري): ").strip()
        ans = input("نص الإجابة: ").strip()
        if ans:
            new_faq = self.admin_service.add_faq(q, ans, q_en)
            print(f"✅ تم حفظ السؤال برقم {new_faq['id']} بنجاح في faqs.json!")
        input("\nاضغط Enter للمتابعة...")

    # ==================================================================
    # AUTOMATED DEMONSTRATION RUN
    # ==================================================================
    def run_demo(self):
        print("\n" + "=" * 72)
        print("⚡ تشغيل تجريبي شامل يوضح كافة متطلبات المشروع")
        print("=" * 72)

        # 1. IR Search Demo
        print("\n[1] تجربة محرك استرجاع المعلومات (TF-IDF + Cosine Similarity):")
        queries = ["مشروع التخرج وساعاته", "Deep Learning Neural Networks", "مكتب العميد والدور"]
        for q in queries:
            print(f"\n🔎 استعلام: '{q}'")
            results = self.student_service.search_academic_information(q, top_k=2)
            for r in results:
                print(f"  • النتيجة: {r['title']} (Score: {r['score']})")
                print(f"    المقتطف: {r['snippet']}")

        # 2. Knowledge Representation & Inference Demo
        print("\n" + "-" * 72)
        print("[2] تجربة محرك الاستدلال وقاعدة المعرفة:")
        rep = self.student_service.check_eligible_courses()
        print(f"الطالب: {rep['student_name']} | الساعات المجتازة: {rep['passed_hours']} | المستوى: {rep['academic_level']}")
        print(f"الحالة الأكاديمية: {rep['academic_standing']}")
        print(f"ساعات التسجيل المسموح بها: {rep['credit_limits']['min_hours']} - {rep['credit_limits']['max_hours']} ساعة ({rep['credit_limits']['notes']})")
        print("المقررات المؤهل لتسجيلها (أول 4):")
        for c in rep["eligible_courses"][:4]:
            print(f"  ✅ [{c['course_code']}] {c['title_ar']} ({c['title_en']})")

        # 3. Check Specific Course & Prerequisite Chain
        print("\n" + "-" * 72)
        print("[3] فحص مقرر محدد وشجرة المتطلبات:")
        test_courses = ["ML211", "GP411"]
        for tc in test_courses:
            res = self.student_service.check_specific_course(tc)
            print(f"  • فحص {tc}: {res.get('reason')}")
        
        tree = self.student_service.get_prerequisite_path("ML311")
        print(f"\n  • مسار متطلبات المقرر المتقدم ML311 (التعلم العميق):")
        for step in tree.get("full_dependency_chain", []):
            print(f"    └── [{step['course_code']}] {step['title_ar']} ➡️ {step['is_direct_prereq_to']}")

        # 4. Check Query Logs
        print("\n" + "-" * 72)
        print("[4] محتويات ملف السجلات queries.log:")
        recent = self.admin_service.view_logs(5)
        for log in recent:
            print(f"  📝 {log}")

        print("\n" + "=" * 72)
        print("✅ اكتمل التشغيل التجريبي بنجاح تام وفقاً لكافة الشروط!")
        input("\nاضغط Enter للمتابعة...")


if __name__ == "__main__":
    app = SmartStudentApp()
    app.main_menu()
