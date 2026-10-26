"""
Smart Student Guide - Modern Web GUI
AI Course Assignment - Task 1: Smart Student Guide
Faculty of Artificial Intelligence - Kafrelsheikh University
Team: Qeset Eshq (قصة عشق)
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
    page_title="Smart Student Guide | فريق قصة عشق",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cohesive Premium Dark Tech UI Styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', 'Plus Jakarta Sans', sans-serif !important;
}

/* App Background */
.stApp {
    background-color: #0b0f19 !important;
    color: #f1f5f9 !important;
}

/* Sidebar Dark Theme Fix */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid #1f2937 !important;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #cbd5e1 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* Hero Header */
.hero-box {
    background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 50%, #4338ca 100%);
    border: 1px solid #4338ca;
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 20px 40px -15px rgba(67, 56, 202, 0.35);
    direction: rtl;
    text-align: right;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #ffffff !important;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.hero-meta {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 10px;
}
.pill-badge {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #ffffff !important;
    padding: 5px 14px;
    border-radius: 30px;
    font-size: 0.82rem;
    font-weight: 700;
    backdrop-filter: blur(6px);
}
.pill-team {
    background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
    border: 1px solid #fda4af;
    color: #ffffff !important;
    padding: 5px 16px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 800;
    box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
}

/* Stat Cards */
.stat-grid-card {
    background: #151c2c;
    border: 1px solid #243048;
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    text-align: right;
    direction: rtl;
    transition: all 0.25s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    position: relative;
    overflow: hidden;
}
.stat-grid-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
}
.stat-grid-card:hover {
    transform: translateY(-3px);
    border-color: #6366f1;
    box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.25);
}
.stat-label-text {
    font-size: 0.85rem;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 0.35rem;
}
.stat-value-text {
    font-size: 1.65rem;
    font-weight: 900;
    color: #f8fafc;
}

/* Result Cards */
.doc-result-card {
    background: #151c2c;
    border: 1px solid #243048;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    text-align: right;
    direction: rtl;
    transition: all 0.25s ease;
}
.doc-result-card:hover {
    border-color: #6366f1;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
}
.doc-result-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
    direction: ltr;
}
.score-chip {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 0.82rem;
    padding: 4px 12px;
    border-radius: 20px;
    box-shadow: 0 2px 10px rgba(79, 70, 229, 0.35);
}
.doc-title-text {
    font-size: 1.15rem;
    font-weight: 800;
    color: #f8fafc;
    text-align: right;
    direction: rtl;
}
.doc-source-chip {
    display: inline-block;
    background: #1e293b;
    color: #94a3b8;
    font-size: 0.8rem;
    padding: 3px 10px;
    border-radius: 8px;
    margin-bottom: 0.7rem;
    font-weight: 600;
    border: 1px solid #334155;
}
.doc-snippet-box {
    background: #0f172a;
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.7;
    padding: 0.9rem 1.1rem;
    border-radius: 12px;
    border-right: 4px solid #6366f1;
    margin-top: 0.5rem;
}

/* Course Pill Cards */
.modern-course-card {
    background: #151c2c;
    border: 1px solid #243048;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    direction: rtl;
    transition: all 0.2s ease;
}
.modern-course-card:hover {
    border-color: #6366f1;
    transform: translateX(-4px);
}
.c-code-badge {
    background: #1e1b4b;
    color: #818cf8;
    border: 1px solid #3730a3;
    font-weight: 800;
    font-size: 0.95rem;
    padding: 4px 12px;
    border-radius: 8px;
    letter-spacing: 0.5px;
}
.c-name-ar {
    font-size: 1.05rem;
    font-weight: 800;
    color: #f8fafc;
    margin-right: 10px;
}
.c-name-en {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-right: 6px;
}
.c-meta-line {
    font-size: 0.83rem;
    color: #64748b;
    margin-top: 5px;
}
.badge-ready {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid #059669;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    white-space: nowrap;
}
.badge-locked {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid #b91c1c;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    white-space: nowrap;
}

/* Tree Lineage */
.lineage-step {
    background: #151c2c;
    border: 1px solid #243048;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    margin: 8px 0;
    border-right: 4px solid #8b5cf6;
    color: #f1f5f9;
    direction: rtl;
    text-align: right;
}

/* Suggestion Pills */
.search-pill-btn {
    display: inline-block;
    background: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.82rem;
    margin-left: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.search-pill-btn:hover {
    background: #312e81;
    border-color: #6366f1;
    color: #ffffff;
}

/* Form & Input adjustments */
.stTextInput>div>div>input {
    background-color: #151c2c !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}
.stSelectbox>div>div {
    background-color: #151c2c !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
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
    <div style="text-align: center; padding: 15px 0 10px 0; border-bottom: 1px solid #1f2937; margin-bottom: 15px;">
        <div style="font-size: 2.8rem; margin-bottom: 5px;">🤖</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: #f8fafc;">Smart Student Guide</div>
        <div style="font-size: 0.82rem; color: #94a3b8;">كلية الذكاء الاصطناعي - كفر الشيخ</div>
        <div style="margin-top: 8px;">
            <span class="pill-team">❤️ فريق: قصة عشق</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    portal = st.radio(
        "اختر واجهة الاستخدام:",
        ["👤 بوابة الطالب (Student Portal)", "🛠️ بوابة الإدارة (Admin Portal)"],
        index=0
    )

    st.markdown("---")

    if portal.startswith("👤"):
        st.markdown("<div style='font-weight: 700; color: #cbd5e1; margin-bottom: 8px;'>⚙️ إعدادات ملف الطالب:</div>", unsafe_allow_html=True)
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
            help="حدد المقررات التي اجتزتها لحساب المواد المتاحة للتسجيل تلقائياً."
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
<div class="hero-box">
    <div class="hero-title">
        <span>🎓 دليل الطالب الأكاديمي الذكي (Smart Student Guide)</span>
    </div>
    <div style="font-size: 1.05rem; color: #cbd5e1; font-weight: 600;">
        كلية الذكاء الاصطناعي — جامعة كفر الشيخ (برنامج عام 2023)
    </div>
    <div class="hero-meta">
        <span class="pill-badge">📌 Task 1: AI Assignment</span>
        <span class="pill-badge">⚡ نظام الساعات المعتمدة</span>
        <span class="pill-team">❤️ فريق العمل: قصة عشق</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# STUDENT PORTAL VIEW
# ==============================================================================
if portal.startswith("👤"):
    rep = student_service.check_eligible_courses()
    passed_hrs = rep["passed_hours"]
    rem_hrs = rep["remaining_hours"]
    pct_grad = min(100.0, round((passed_hrs / 144.0) * 100, 1))

    # Metric Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">المستوى الأكاديمي</div>
            <div class="stat-value-text">{rep["academic_level"].split()[0]} {rep["academic_level"].split()[1]}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">الساعات المجتازة / 144</div>
            <div class="stat-value-text">{passed_hrs} <span style="font-size:0.9rem; color:#94a3b8;">ساعة</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">المعدل التراكمي CGPA</div>
            <div class="stat-value-text">{cgpa:.2f} <span style="font-size:0.9rem; color:#818cf8;">/ 4.0</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        limits = rep["credit_limits"]
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">العبء المسموح للفصل القادم</div>
            <div class="stat-value-text">{limits['min_hours']} - {limits['max_hours']} <span style="font-size:0.9rem; color:#94a3b8;">ساعة</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Progress bar
    st.markdown(f"""
    <div style="direction: rtl; text-align: right; margin: 1.3rem 0 0.4rem 0; font-size: 0.88rem; font-weight: 700; color: #94a3b8;">
        نسبة إنجاز ساعات التخرج ({passed_hrs} من 144 ساعة — {pct_grad}%):
    </div>
    """, unsafe_allow_html=True)
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
        "❓ فحص مقرر وشجرة المتطلبات",
        "💡 الأسئلة الشائعة (FAQs)"
    ])

    # -------------------------------------------------------------
    # TAB 1: INFORMATION RETRIEVAL
    # -------------------------------------------------------------
    with tab1:
        st.markdown("### 🔍 محرك استرجاع المعلومات (Inverted Index + TF-IDF + Cosine Similarity)")
        st.caption("ابحث باللغة العربية أو الإنجليزية في لوائح الكلية الأكاديمية، توصيف المقررات، بيانات أعضاء هيئة التدريس، والمعامل.")

        col_search, col_k = st.columns([5, 1])
        with col_search:
            query = st.text_input(
                "اكتب استفسارك هنا:",
                value="مشروع التخرج وساعاته",
                placeholder="أمثلة: شروط التسجيل، الإنذار الأكاديمي، مكتب العميد، معمل الروبوتات، Deep learning..."
            )
        with col_k:
            top_k = st.selectbox("عدد النتائج:", [3, 5, 8], index=0)

        # Quick Suggestion Tags
        st.markdown("""
        <div style="direction: rtl; text-align: right; margin-bottom: 15px;">
            <span style="font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-left: 8px;">مقترحات سريعة للبحث:</span>
            <span class="search-pill-btn">مشروع التخرج</span>
            <span class="search-pill-btn">الإنذار الأكاديمي</span>
            <span class="search-pill-btn">مرتبة الشرف</span>
            <span class="search-pill-btn">معمل الروبوتات</span>
            <span class="search-pill-btn">مكتب العميد</span>
            <span class="search-pill-btn">Deep Learning</span>
        </div>
        """, unsafe_allow_html=True)

        if query.strip():
            results = student_service.search_academic_information(query, top_k=top_k)
            if not results:
                st.warning("لم يتم العثور على وثائق مطابقة لاستفسارك.")
            else:
                st.markdown(f"**تم العثور على ({len(results)}) نتائج مرتبة حسب درجة التطابق (Cosine Similarity):**")
                for r in results:
                    score_pct = round(r['score'] * 100, 1)
                    st.markdown(f"""
                    <div class="doc-result-card">
                        <div class="doc-result-top">
                            <span class="score-chip">Cosine Sim: {r['score']:.4f} ({score_pct}%)</span>
                            <span class="doc-title-text">📄 {r['title']}</span>
                        </div>
                        <span class="doc-source-chip">📁 المصدر: {r['source_file']}</span>
                        <div class="doc-snippet-box">{r['snippet']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 عرض النص الكامل للوثيقة"):
                        st.write(r["text"])

    # -------------------------------------------------------------
    # TAB 2: ELIGIBILITY INFERENCE
    # -------------------------------------------------------------
    with tab2:
        st.markdown("### 📋 المقررات المؤهل لتسجيلها (Forward Chaining Inference)")
        st.caption(f"استنتاج مبني على المقررات المنجزة ({len(passed_selected)} مقرر) ومعدلك التراكمي ({cgpa:.2f}).")

        eligible = rep["eligible_courses"]
        locked = rep["locked_courses"]

        st.markdown(f"#### 🟢 المقررات المتاحة للتسجيل الآن ({len(eligible)} مقرر):")
        if not eligible:
            st.warning("لا توجد مقررات متاحة حالياً.")
        else:
            for c in eligible:
                prereqs = ", ".join(c["prerequisites_satisfied"]) if c["prerequisites_satisfied"] else "بدون متطلب"
                st.markdown(f"""
                <div class="modern-course-card">
                    <div>
                        <span class="c-code-badge">{c['course_code']}</span>
                        <span class="c-name-ar">{c['title_ar']}</span>
                        <span class="c-name-en">({c['title_en']})</span>
                        <div class="c-meta-line">
                            الساعات: <b>{c['credit_hours']}</b> | المستوى: <b>{c['level']}</b> | القسم: <b>{c['department']}</b> | النوع: <b>{c['course_type']}</b>
                        </div>
                    </div>
                    <div>
                        <span class="badge-ready">✓ مستوفى: {prereqs}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander(f"🔒 عرض المقررات المقفلة لعدم استيفاء المتطلبات ({len(locked)} مقرر)"):
            for c in locked:
                missing = ", ".join(c["missing_prerequisites"])
                st.markdown(f"""
                <div class="modern-course-card" style="opacity: 0.8; border-color: #451a1a;">
                    <div>
                        <span class="c-code-badge" style="background:#451a1a; color:#f87171; border-color:#7f1d1d;">{c['course_code']}</span>
                        <span class="c-name-ar">{c['title_ar']}</span>
                        <span class="c-name-en">({c['title_en']})</span>
                        <div class="c-meta-line">المستوى: {c['level']} | الساعات: {c['credit_hours']}</div>
                    </div>
                    <div>
                        <span class="badge-locked">⚠️ يتطلب: {missing}</span>
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
                <div style="background:#064e3b; border:1px solid #059669; border-radius:12px; padding:15px; margin: 15px 0; direction: rtl; text-align: right;">
                    <h4 style="color:#6ee7b7; margin:0 0 5px 0;">✅ مؤهل لتسجيل المقرر بنجاح!</h4>
                    <p style="color:#d1fae5; margin:0;">{res.get('reason')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#450a0a; border:1px solid #b91c1c; border-radius:12px; padding:15px; margin: 15px 0; direction: rtl; text-align: right;">
                    <h4 style="color:#fca5a5; margin:0 0 5px 0;">❌ غير مؤهل للتسجيل حالياً</h4>
                    <p style="color:#fee2e2; margin:0;">{res.get('reason')}</p>
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
                        <div class="lineage-step">
                            <b>[{step['course_code']}]</b> {step['title_ar']} ({step['title_en']})
                            <span style="color:#a855f7; font-weight:800; margin: 0 8px;">⬅️ مطلوب لفتح ➡️</span>
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
        <div class="stat-grid-card">
            <div class="stat-label-text">إجمالي المقررات</div>
            <div class="stat-value-text">{stats['total_courses']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">المقاطع المفهرسة (IR)</div>
            <div class="stat-value-text">{stats['indexed_passages']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">الأسئلة الشائعة</div>
            <div class="stat-value-text">{stats['total_faqs']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="stat-grid-card">
            <div class="stat-label-text">الاستعلامات المسجلة</div>
            <div class="stat-value-text">{stats['logged_queries_count']}</div>
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

# Footer
st.markdown("""
<div style="direction: rtl; text-align: center; color: #64748b; font-size: 0.88rem; padding: 30px 0 15px 0; border-top: 1px solid #1f2937; margin-top: 40px;">
    تم التطوير وتصميم النظام بواسطة فريق <b style="color: #f43f5e;">قصة عشق ❤️</b> — مقرر الذكاء الاصطناعي (جامعة كفر الشيخ) 2026
</div>
""", unsafe_allow_html=True)
