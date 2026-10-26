"""
Smart Student Guide - Modern Web GUI
AI Course Assignment - Task 1: Smart Student Guide
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

# Page Configuration
st.set_page_config(
    page_title="Smart Student Guide | Task 1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern CSS Styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background & Smooth Scrolling */
.main {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Modern Hero Header */
.hero-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
    color: white;
    padding: 2.2rem 2.5rem;
    border-radius: 20px;
    box-shadow: 0 15px 35px -5px rgba(49, 46, 129, 0.25);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.hero-header::after {
    content: "";
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 1.05rem;
    opacity: 0.9;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 12px;
}
.badge-task {
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

/* Stat Cards */
.stat-card {
    background: white;
    padding: 1.25rem 1.4rem;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
    transition: all 0.25s ease;
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px -4px rgba(79, 70, 229, 0.12);
    border-color: #c7d2fe;
}
.stat-label {
    font-size: 0.85rem;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0f172a;
}

/* Search Result Cards */
.result-card {
    background: white;
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1.2rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease;
}
.result-card:hover {
    border-color: #818cf8;
    box-shadow: 0 10px 25px -3px rgba(99, 102, 241, 0.12);
}
.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}
.result-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e1b4b;
}
.score-badge {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    color: white;
    font-weight: 700;
    font-size: 0.82rem;
    padding: 4px 12px;
    border-radius: 30px;
    letter-spacing: 0.5px;
}
.result-source {
    display: inline-block;
    font-size: 0.78rem;
    color: #475569;
    background: #f1f5f9;
    padding: 2px 10px;
    border-radius: 12px;
    margin-bottom: 0.6rem;
    font-weight: 600;
}
.result-snippet {
    color: #334155;
    font-size: 0.95rem;
    line-height: 1.65;
    background: #f8fafc;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    border-right: 4px solid #6366f1;
}

/* Course Pill Card */
.course-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s ease;
}
.course-card:hover {
    transform: translateX(-4px);
    border-color: #a5b4fc;
}
.course-code {
    font-weight: 800;
    font-size: 1.05rem;
    color: #4338ca;
    background: #eef2ff;
    padding: 4px 10px;
    border-radius: 8px;
    display: inline-block;
}
.course-name {
    font-weight: 700;
    font-size: 1rem;
    color: #1e293b;
    margin-right: 8px;
}
.course-meta {
    font-size: 0.83rem;
    color: #64748b;
    margin-top: 3px;
}
.tag-prereq {
    background: #ecfdf5;
    color: #065f46;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
}
.tag-locked {
    background: #fef2f2;
    color: #991b1b;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* Tree Nodes */
.tree-node {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 0.7rem 1.2rem;
    border-radius: 12px;
    margin: 6px 0;
    border-right: 4px solid #4f46e5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize System Cache
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


# Sidebar Configuration
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <div style="font-size: 2.8rem; line-height: 1;">🤖</div>
        <h3 style="margin: 8px 0 2px 0; font-weight: 800; color: #1e1b4b;">Smart Student Guide</h3>
        <p style="margin: 0; font-size: 0.85rem; color: #64748b;">كلية الذكاء الاصطناعي - كفر الشيخ</p>
    </div>
    """, unsafe_allow_html=True)

    portal = st.radio(
        "اختر واجهة الاستخدام:",
        ["👤 بوابة الطالب (Student Portal)", "🛠️ بوابة الإدارة (Admin Portal)"],
        index=0
    )

    st.markdown("---")

    if portal.startswith("👤"):
        st.markdown("#### ⚙️ إعدادات ملف الطالب")
        student_id = st.text_input("رقم الجلوس / الكود:", value="2023001")
        student_name = st.text_input("اسم الطالب:", value="Zeyad")
        cgpa = st.slider("المعدل التراكمي (CGPA):", min_value=0.5, max_value=4.0, value=3.40, step=0.05)
        semesters = st.number_input("الفصول المكتملة:", min_value=1, max_value=8, value=1)
        
        all_courses = fm.load_courses()
        all_codes = [c["course_code"] for c in all_courses]
        
        default_passed = ["MA111", "MA112", "MA113", "HU111", "MA114", "BC111", "MA115", "MA116"]
        passed_selected = st.multiselect(
            "المقررات المجتازة (Passed Courses):",
            options=all_codes,
            default=[c for c in default_passed if c in all_codes],
            help="حدد المقررات التي نجحت فيها لحساب المواد المتاحة للتسجيل تلقائياً."
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
    else:
        current_student = None
        student_service = None

# ==============================================================================
# HERO HEADER
# ==============================================================================
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎓 دليل الطالب الأكاديمي الذكي (Smart Student Guide)</div>
    <div class="hero-subtitle">
        <span>مقرر الذكاء الاصطناعي — كلية الذكاء الاصطناعي (جامعة كفر الشيخ)</span>
        <span class="badge-task">Task 1: AI Assignment</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# STUDENT PORTAL VIEW
# ==============================================================================
if portal.startswith("👤"):
    # Real-time inference stats
    rep = student_service.check_eligible_courses()
    passed_hrs = rep["passed_hours"]
    rem_hrs = rep["remaining_hours"]
    pct_grad = min(100.0, round((passed_hrs / 144.0) * 100, 1))

    # Metric Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">المستوى الأكاديمي</div>
            <div class="stat-value">{rep["academic_level"].split()[0]} {rep["academic_level"].split()[1]}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">الساعات المجتازة / 144</div>
            <div class="stat-value">{passed_hrs} <span style="font-size:0.9rem; color:#64748b;">ساعة</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">المعدل التراكمي CGPA</div>
            <div class="stat-value">{cgpa:.2f} <span style="font-size:0.85rem; color:#4f46e5;">/ 4.0</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        limits = rep["credit_limits"]
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">العبء المسموح للفصل القادم</div>
            <div class="stat-value">{limits['min_hours']} - {limits['max_hours']} <span style="font-size:0.9rem; color:#64748b;">ساعة</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Progress toward graduation
    st.markdown(f"<div style='margin: 1.2rem 0 0.4rem 0; font-size: 0.88rem; font-weight: 700; color: #475569;'>نسبة إنجاز ساعات التخرج ({passed_hrs} من 144 ساعة - {pct_grad}%):</div>", unsafe_allow_html=True)
    st.progress(pct_grad / 100.0)

    # Academic Alert / Standing Banner
    if "Probation" in rep["academic_standing"]:
        st.error(f"⚠️ **{rep['academic_standing']}** — {rep['probation_alert']}")
    else:
        st.success(f"✅ **{rep['academic_standing']}** — {rep['probation_alert']}")

    st.write("")

    # Modern Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 البحث الذكي في اللائحة (IR)",
        "📋 المقررات المتاحة للتسجيل (Inference)",
        "❓ فحص مقرر محدد وشجرة المتطلبات",
        "💡 الأسئلة الشائعة (FAQs)"
    ])

    # -------------------------------------------------------------
    # TAB 1: INFORMATION RETRIEVAL
    # -------------------------------------------------------------
    with tab1:
        st.markdown("### 🔍 محرك استرجاع المعلومات (Inverted Index + TF-IDF + Cosine Similarity)")
        st.caption("ابحث في لوائح الكلية الأكاديمية، توصيف المقررات، بيانات أعضاء هيئة التدريس، ومواقع القاعات والمعامل.")

        col_search, col_k = st.columns([5, 1])
        with col_search:
            query = st.text_input(
                "اكتب استفسارك باللغة العربية أو الإنجليزية:",
                value="مشروع التخرج وساعاته",
                placeholder="أمثلة: شروط التسجيل، الإنذار الأكاديمي، مكتب العميد، معمل الروبوتات، Deep learning..."
            )
        with col_k:
            top_k = st.selectbox("عدد النتائج:", [3, 5, 8], index=0)

        # Quick Suggestion Pills
        st.markdown("""
        <div style="display:flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #64748b; padding-top: 4px;">مقترحات سريعة:</span>
            <span style="background: #e2e8f0; color:#334155; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; cursor: pointer;">مشروع التخرج</span>
            <span style="background: #e2e8f0; color:#334155; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; cursor: pointer;">الإنذار الأكاديمي</span>
            <span style="background: #e2e8f0; color:#334155; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; cursor: pointer;">مرتبة الشرف</span>
            <span style="background: #e2e8f0; color:#334155; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; cursor: pointer;">معمل الذكاء الاصطناعي</span>
            <span style="background: #e2e8f0; color:#334155; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; cursor: pointer;">Deep Learning</span>
        </div>
        """, unsafe_allow_html=True)

        if query.strip():
            results = student_service.search_academic_information(query, top_k=top_k)
            if not results:
                st.warning("لم يتم العثور على وثائق مطابقة لاستفسارك.")
            else:
                st.markdown(f"**تم العثور على ({len(results)}) وثائق مرتبة حسب تشابه جيب التمام (Cosine Similarity):**")
                for r in results:
                    score_pct = round(r['score'] * 100, 1)
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-header">
                            <span class="result-title">📄 {r['title']}</span>
                            <span class="score-badge">Similarity: {r['score']:.4f} ({score_pct}%)</span>
                        </div>
                        <span class="result-source">📁 الملف المصدر: {r['source_file']}</span>
                        <div class="result-snippet">{r['snippet']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 عرض النص الكامل للوثيقة"):
                        st.write(r["text"])

    # -------------------------------------------------------------
    # TAB 2: ELIGIBILITY INFERENCE
    # -------------------------------------------------------------
    with tab2:
        st.markdown("### 📋 المقررات المؤهل لتسجيلها (Forward Chaining Inference)")
        st.markdown(f"استنتاج مبني على المقررات المنجزة ({len(passed_selected)} مقرر) ومعدلك التراكمي ({cgpa:.2f}).")

        eligible = rep["eligible_courses"]
        locked = rep["locked_courses"]

        st.markdown(f"#### 🟢 المقررات المتاحة للتسجيل الآن ({len(eligible)} مقرر):")
        if not eligible:
            st.warning("لا توجد مقررات متاحة حالياً.")
        else:
            for c in eligible:
                prereqs = ", ".join(c["prerequisites_satisfied"]) if c["prerequisites_satisfied"] else "بدون متطلب"
                st.markdown(f"""
                <div class="course-card">
                    <div>
                        <span class="course-code">{c['course_code']}</span>
                        <span class="course-name">{c['title_ar']} ({c['title_en']})</span>
                        <div class="course-meta">
                            الساعات: <b>{c['credit_hours']}</b> | المستوى: <b>{c['level']}</b> | القسم: <b>{c['department']}</b> | النوع: <b>{c['course_type']}</b>
                        </div>
                    </div>
                    <div>
                        <span class="tag-prereq">✓ المتطلب مستوفى: {prereqs}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander(f"🔒 عرض المقررات المقفلة لعدم استيفاء المتطلبات ({len(locked)} مقرر)"):
            for c in locked:
                missing = ", ".join(c["missing_prerequisites"])
                st.markdown(f"""
                <div class="course-card" style="opacity: 0.85; border-color: #fecdd3;">
                    <div>
                        <span class="course-code" style="background:#ffe4e6; color:#9f1239;">{c['course_code']}</span>
                        <span class="course-name">{c['title_ar']} ({c['title_en']})</span>
                        <div class="course-meta">المستوى: {c['level']} | الساعات: {c['credit_hours']}</div>
                    </div>
                    <div>
                        <span class="tag-locked">⚠️ يتطلب: {missing}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: SINGLE COURSE & DEPENDENCY TREE
    # -------------------------------------------------------------
    with tab3:
        st.markdown("### ❓ التحقق من مقرر محدد وتتبع شجرة المتطلبات")
        chk_col1, chk_col2 = st.columns([4, 1])
        with chk_col1:
            sel_course = st.selectbox(
                "اختر كود المقرر للفحص الأكاديمي:",
                options=all_codes,
                index=all_codes.index("ML211") if "ML211" in all_codes else 0
            )
        with chk_col2:
            st.write("")
            st.write("")
            chk_btn = st.button("فحص الأهلية", use_container_width=True)

        if sel_course:
            res = student_service.check_specific_course(sel_course)
            if res.get("can_register"):
                st.markdown(f"""
                <div style="background:#ecfdf5; border:1px solid #6ee7b7; border-radius:12px; padding:15px; margin: 15px 0;">
                    <h4 style="color:#065f46; margin:0 0 5px 0;">✅ مؤهل لتسجيل المقرر بنجاح!</h4>
                    <p style="color:#047857; margin:0;">{res.get('reason')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#fef2f2; border:1px solid #fca5a5; border-radius:12px; padding:15px; margin: 15px 0;">
                    <h4 style="color:#991b1b; margin:0 0 5px 0;">❌ غير مؤهل للتسجيل حالياً</h4>
                    <p style="color:#b91c1c; margin:0;">{res.get('reason')}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 🌳 مسار المتطلبات التراكمية (Prerequisite Dependency Lineage):")
            tree = student_service.get_prerequisite_path(sel_course)
            chain = tree.get("full_dependency_chain", [])
            if not chain:
                st.info("💡 هذا المقرر لا يتطلب أي مقررات سابقة (مقرر مستوى أول أو حر).")
            else:
                for step in chain:
                    indent_px = step["depth"] * 24
                    st.markdown(f"""
                    <div style="margin-right: {indent_px}px;">
                        <div class="tree-node">
                            <b>[{step['course_code']}]</b> {step['title_ar']} ({step['title_en']})
                            <span style="color:#6366f1; font-weight:700; margin-right:8px;">⬅️ مطلوب لفتح ➡️</span>
                            <b>[{step['is_direct_prereq_to']}]</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 4: FAQS
    # -------------------------------------------------------------
    with tab4:
        st.markdown("### 💡 الأسئلة الشائعة للكلية (FAQs)")
        faqs = student_service.get_faqs()
        for f in faqs:
            with st.expander(f"❓ {f['question']}"):
                st.markdown(f"**الإجابة:** {f['answer']}")
                if "question_en" in f and f["question_en"]:
                    st.caption(f"EN: {f['question_en']}")

# ==============================================================================
# ADMIN PORTAL VIEW
# ==============================================================================
else:
    stats = admin_service.get_stats()
    st.markdown("### 🛠️ لوحة تحكم المسؤول الأكاديمي (Admin Portal)")
    st.caption("إدارة مقررات اللائحة، الوثائق، الأسئلة الشائعة، ومتابعة سجلات الطلاب.")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">إجمالي المقررات</div>
            <div class="stat-value">{stats['total_courses']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">المقاطع المفهرسة (IR)</div>
            <div class="stat-value">{stats['indexed_passages']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">الأسئلة الشائعة</div>
            <div class="stat-value">{stats['total_faqs']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">الاستعلامات المسجلة</div>
            <div class="stat-value">{stats['logged_queries_count']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
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
            submitted = st.form_submit_button("حفظ المقرر الجديد في CSV و JSON")

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
                        st.rerun()
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
