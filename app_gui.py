"""
Smart Student Guide - Interactive Web GUI (Streamlit)
Faculty of Artificial Intelligence - Kafrelsheikh University
"""

import streamlit as st
import os
import sys

# Ensure UTF-8
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


st.set_page_config(
    page_title="Smart Student Guide | دليل الطالب الذكي",
    page_icon="🎓",
    layout="wide"
)

# Initialize Session State
@st.cache_resource
def load_system():
    fm = FileManager()
    ir_index = InvertedIndex()
    ir_index.load_from_directory(fm.docs_dir)
    courses = fm.load_courses()
    engine = AcademicInferenceEngine(fm.kb_json, courses)
    admin = AdminService(fm, ir_index)
    return fm, ir_index, engine, admin

fm, ir_index, engine, admin_service = load_system()

# Sidebar: Portal Switch & Student Profile Setup
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=90)
st.sidebar.title("🎓 Smart Student Guide")
st.sidebar.caption("كلية الذكاء الاصطناعي - جامعة كفر الشيخ")

portal = st.sidebar.radio("اختر الواجهة (Select Portal):", ["👤 Student Portal (بوابة الطالب)", "🛠️ Admin Portal (بوابة الإدارة)"])

st.sidebar.markdown("---")

if portal.startswith("👤"):
    st.sidebar.subheader("📌 بيانات الطالب الأكاديمية")
    student_id = st.sidebar.text_input("رقم الطالب الجامعي:", value="2023001")
    student_name = st.sidebar.text_input("اسم الطالب:", value="Zeyad")
    cgpa = st.sidebar.slider("المعدل التراكمي CGPA:", min_value=0.5, max_value=4.0, value=3.40, step=0.05)
    semesters = st.sidebar.number_input("الفصول المكتملة:", min_value=1, max_value=8, value=1)
    
    all_courses = fm.load_courses()
    all_codes = [c["course_code"] for c in all_courses]
    
    default_passed = ["MA111", "MA112", "MA113", "HU111", "MA114", "BC111", "MA115", "MA116"]
    passed_selected = st.sidebar.multiselect(
        "المقررات المجتازة بنجاح (Passed Courses):",
        options=all_codes,
        default=[c for c in default_passed if c in all_codes]
    )

    current_student = StudentProfile(
        student_id=student_id,
        name=student_name,
        passed_courses=passed_selected,
        cgpa=cgpa,
        completed_semesters=semesters,
        is_freshman_first_term=(semesters == 1 and len(passed_selected) == 0)
    )
    student_service = StudentService(fm, ir_index, engine, current_student)

    # -------------------------------------------------------------
    # STUDENT PORTAL VIEW
    # -------------------------------------------------------------
    st.title("🎓 دليل الطالب الأكاديمي الذكي")
    st.write(f"مرحباً بك، **{student_name}** | مرحلة البكالوريوس بنظام الساعات المعتمدة")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 البحث في اللائحة والوثائق (IR)",
        "📋 استدلال المقررات المتاحة للتسجيل (Inference)",
        "❓ فحص مقرر وشجرة المتطلبات",
        "💡 الأسئلة الشائعة (FAQs)"
    ])

    # Tab 1: Information Retrieval
    with tab1:
        st.subheader("🔍 محرك استرجاع المعلومات الأكاديمية (TF-IDF & Cosine Similarity)")
        st.caption("ابحث في لوائح الكلية، توصيف المقررات، بيانات أعضاء هيئة التدريس، والقاعات والمعامل.")
        
        col_q, col_k = st.columns([4, 1])
        with col_q:
            query = st.text_input("اكتب سؤالك أو موضوع البحث:", value="مشروع التخرج وساعاته", placeholder="مثال: شروط الإنذار الأكاديمي، مكتب العميد، معمل الروبوتات، Deep Learning...")
        with col_k:
            top_k = st.selectbox("عدد النتائج:", [3, 5, 8], index=0)

        if st.button("🔎 ابحث الآن", use_container_width=True):
            if query.strip():
                results = student_service.search_academic_information(query, top_k=top_k)
                if not results:
                    st.warning("لم يتم العثور على نتائج مطابقة لهذا الاستعلام.")
                else:
                    st.success(f"تم العثور على {len(results)} نتائج مرتبة حسب درجة التطابق (Cosine Similarity):")
                    for r in results:
                        with st.expander(f"📄 {r['title']}  —  (Similarity Score: {r['score']:.4f})", expanded=True):
                            st.markdown(f"**المصدر:** `{r['source_file']}`")
                            st.info(f"**مقتطف:** {r['snippet']}")
                            with st.expander("عرض النص الكامل للمقطع"):
                                st.write(r["text"])

    # Tab 2: Eligibility Inference
    with tab2:
        st.subheader("📋 تقرير استدلال التسجيل والحالة الأكاديمية")
        rep = student_service.check_eligible_courses()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("المستوى الأكاديمي", rep["academic_level"].split()[0])
        col2.metric("الساعات المجتازة", f"{rep['passed_hours']} ساعة")
        col3.metric("المتبقي للتخرج", f"{rep['remaining_hours']} ساعة")
        col4.metric("المعدل التراكمي", f"{cgpa:.2f}")

        # Standing alert
        if "Probation" in rep["academic_standing"]:
            st.error(f"⚠️ {rep['probation_alert']}")
        else:
            st.success(f"✅ الوضع الأكاديمي سليم: {rep['probation_alert']}")

        st.info(f"📌 **حدود ساعات التسجيل للفصل القادم:** الحد الأدنى: **{rep['credit_limits']['min_hours']}** ساعات | الحد الأقصى: **{rep['credit_limits']['max_hours']}** ساعة ({rep['credit_limits']['notes']})")

        st.markdown("### 🟢 المقررات المتاح لك تسجيلها الآن:")
        eligible = rep["eligible_courses"]
        if eligible:
            st.dataframe(
                [
                    {
                        "الكود": c["course_code"],
                        "اسم المقرر بالعربية": c["title_ar"],
                        "Course Title": c["title_en"],
                        "الساعات": c["credit_hours"],
                        "المستوى": c["level"],
                        "القسم": c["department"],
                        "المتطلب السابق": ", ".join(c["prerequisites_satisfied"]) if c["prerequisites_satisfied"] else "بدون متطلب"
                    }
                    for c in eligible
                ],
                use_container_width=True
            )
        else:
            st.warning("لا توجد مقررات متاحة حالياً.")

        with st.expander(f"🔒 عرض المقررات المقفلة لعدم استيفاء الشروط ({len(rep['locked_courses'])} مقرر)"):
            st.dataframe(
                [
                    {
                        "الكود": c["course_code"],
                        "اسم المقرر": c["title_ar"],
                        "المتطلبات الناقصة": ", ".join(c["missing_prerequisites"])
                    }
                    for c in rep["locked_courses"]
                ],
                use_container_width=True
            )

    # Tab 3: Single Course & Dependency Tree
    with tab3:
        st.subheader("❓ فحص مقرر محدد وتتبع شجرة المتطلبات")
        chk_col1, chk_col2 = st.columns([3, 1])
        with chk_col1:
            sel_course = st.selectbox("اختر المقرر الدراسي:", options=all_codes, index=all_codes.index("ML211") if "ML211" in all_codes else 0)
        with chk_col2:
            st.write("")
            st.write("")
            chk_btn = st.button("تحقق الآن", use_container_width=True)

        if sel_course:
            res = student_service.check_specific_course(sel_course)
            if res.get("can_register"):
                st.success(f"✅ {res.get('reason')}")
            else:
                st.error(f"❌ {res.get('reason')}")

            st.markdown("#### 🌳 مسار المتطلبات التراكمية (Prerequisite Lineage Tree):")
            tree = student_service.get_prerequisite_path(sel_course)
            chain = tree.get("full_dependency_chain", [])
            if not chain:
                st.write("• هذا المقرر لا يعتمد على أي متطلبات سابقة (مقرر مستوى أول أو حر).")
            else:
                for step in chain:
                    st.markdown(f"{'&nbsp;' * (step['depth'] * 4)} └── **[{step['course_code']}]** {step['title_ar']} ({step['title_en']}) ➡️ يفتح **[{step['is_direct_prereq_to']}]**")

    # Tab 4: FAQs
    with tab4:
        st.subheader("💡 الأسئلة الشائعة للكلية (FAQs)")
        faqs = student_service.get_faqs()
        for f in faqs:
            with st.expander(f"❓ {f['question']}"):
                st.write(f"**الإجابة:** {f['answer']}")
                if "question_en" in f:
                    st.caption(f"EN: {f['question_en']}")

else:
    # -------------------------------------------------------------
    # ADMIN PORTAL VIEW
    # -------------------------------------------------------------
    st.title("🛠️ لوحة تحكم المسؤول الأكاديمي (Admin Portal)")
    stats = admin_service.get_stats()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("إجمالي المقررات", stats["total_courses"])
    m2.metric("المقاطع المفهرسة (IR)", stats["indexed_passages"])
    m3.metric("الأسئلة الشائعة", stats["total_faqs"])
    m4.metric("الاستعلامات المسجلة", stats["logged_queries_count"])

    atab1, atab2, atab3, atab4, atab5 = st.tabs([
        "📚 المقررات الدراسية",
        "➕ إضافة مقرر جديد",
        "📝 إدارة وثائق اللائحة (TXT)",
        "💡 إدارة الأسئلة الشائعة",
        "📜 سجل الاستعلامات (queries.log)"
    ])

    with atab1:
        st.subheader("📚 قائمة كافة المقررات الدراسية باللائحة")
        courses_data = admin_service.list_courses()
        st.dataframe(courses_data, use_container_width=True)

    with atab2:
        st.subheader("➕ إضافة مقرر دراسي جديد للائحة")
        with st.form("add_course_form"):
            c_code = st.text_input("كود المقرر (مثال: AI450):")
            c_ar = st.text_input("اسم المقرر بالعربية:")
            c_en = st.text_input("اسم المقرر بالإنجليزية:")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                credits = st.number_input("الساعات المعتمدة:", min_value=0, max_value=6, value=3)
            with col_c2:
                lect = st.number_input("ساعات المحاضرة:", min_value=0, max_value=4, value=2)
            with col_c3:
                lab = st.number_input("ساعات العملي:", min_value=0, max_value=4, value=2)
            
            col_c4, col_c5 = st.columns(2)
            with col_c4:
                dept = st.selectbox("القسم:", ["ML", "RB", "ES", "BC", "HU", "MA", "GP"])
                lvl = st.selectbox("المستوى:", [1, 2, 3, 4], index=3)
            with col_c5:
                ctype = st.selectbox("النوع:", ["Core", "Elective"])
                sem = st.selectbox("الفصل الدراسي:", [1, 2], index=1)

            prereq = st.text_input("المتطلب السابق (كود المقرر أو None):", value="None")
            submitted = st.form_submit_button("حفظ المقرر الجديد")

            if submitted:
                if c_code and c_ar:
                    ok = admin_service.add_course(
                        course_code=c_code,
                        title_en=c_en,
                        title_ar=c_ar,
                        credit_hours=credits,
                        lecture_hours=lect,
                        lab_hours=lab,
                        course_type=ctype,
                        department=dept,
                        prerequisite=prereq,
                        level=lvl,
                        semester=sem
                    )
                    if ok:
                        st.success(f"تمت إضافة المقرر {c_code} بنجاح إلى CSV وقاعدة المعرفة!")
                        st.experimental_rerun()
                    else:
                        st.error("المقرر موجود بالفعل أو حدث خطأ.")

    with atab3:
        st.subheader("📝 استعراض وتعديل وثائق اللائحة النصية (TXT)")
        docs = admin_service.list_documents()
        sel_doc = st.selectbox("اختر الوثيقة:", options=docs)
        if sel_doc:
            doc_content = admin_service.read_document(sel_doc)
            edited = st.text_area("محتوى الوثيقة:", value=doc_content, height=350)
            if st.button("حفظ التعديلات وإعادة فهرسة Inverted Index"):
                admin_service.save_document(sel_doc, edited)
                st.success("تم حفظ التعديلات وإعادة بناء الفهرس المعكوس بنجاح!")

    with atab4:
        st.subheader("💡 إضافة سؤال شائع جديد")
        with st.form("faq_form"):
            fq = st.text_input("نص السؤال:")
            fq_en = st.text_input("السؤال بالإنجليزية (اختياري):")
            fa = st.text_area("الإجابة الرسمية:")
            faq_sub = st.form_submit_button("إضافة السؤال")
            if faq_sub and fq and fa:
                new_f = admin_service.add_faq(fq, fa, fq_en)
                st.success(f"تمت إضافة السؤال بنجاح برقم {new_f['id']}!")

    with atab5:
        st.subheader("📜 سجل الاستعلامات والعمليات الفعلي (queries.log)")
        logs = admin_service.view_logs(50)
        st.text_area("أحدث السجلات:", value="\n".join(logs), height=400)
