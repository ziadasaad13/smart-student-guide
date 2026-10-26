"""
Smart Student Guide - Next-Gen Modern Web GUI
AI Course Assignment - Task 1: Smart Student Guide
Faculty of Artificial Intelligence - Kafrelsheikh University
Team: Qeset Eshq (قصة عشق)
"""

import streamlit as st
import os
import sys
import json

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
    page_title="دليل الطالب الذكي | فريق قصة عشق",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# World-Class Next-Gen CSS Styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Font & Layout Reset */
*, html, body, [class*="css"], [class*="st-"] {
    font-family: 'IBM Plex Sans Arabic', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
}

/* Background */
.stApp {
    background-color: #07090e !important;
    color: #f3f4f6 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0d1117;
}
::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #6366f1;
}

/* Modern Tab Navigation Pills */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: #0f141f !important;
    padding: 6px !important;
    border-radius: 16px !important;
    border: 1px solid #1f293d !important;
    direction: rtl !important;
}
.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    border-radius: 12px !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0 18px !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.04) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Sidebar Theme */
[data-testid="stSidebar"] {
    background: #0b0f17 !important;
    border-left: 1px solid #182030 !important;
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5) !important;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #1f293d !important;
}

/* Sleek Hero Banner */
.hero-container {
    background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.18) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 40%),
                linear-gradient(135deg, #0d1220 0%, #111827 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 22px;
    padding: 2.2rem 2.6rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
    direction: rtl;
    text-align: right;
    position: relative;
    overflow: hidden;
}
.hero-title-main {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.5rem;
    line-height: 1.3;
}
.hero-sub-text {
    font-size: 1.05rem;
    color: #94a3b8;
    font-weight: 500;
    margin-bottom: 1rem;
}
.hero-badges-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}
.pill-neutral {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #e2e8f0;
    padding: 5px 14px;
    border-radius: 30px;
    font-size: 0.82rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
}
.pill-team-flair {
    background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
    color: #ffffff;
    padding: 5px 16px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 800;
    box-shadow: 0 4px 15px rgba(244, 63, 94, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Metric / Stat Cards */
.metric-box {
    background: #0f1523;
    border: 1px solid #1e293d;
    border-radius: 18px;
    padding: 1.3rem 1.4rem;
    text-align: right;
    direction: rtl;
    transition: all 0.25s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
}
.metric-box::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #ec4899);
}
.metric-box:hover {
    transform: translateY(-4px);
    border-color: #6366f1;
    box-shadow: 0 12px 30px -5px rgba(99, 102, 241, 0.3);
}
.metric-label-txt {
    font-size: 0.86rem;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 0.35rem;
}
.metric-val-txt {
    font-size: 1.75rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}

/* Result Cards */
.result-card-box {
    background: #0f1523;
    border: 1px solid #1f293d;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    text-align: right;
    direction: rtl;
    transition: all 0.25s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}
.result-card-box:hover {
    border-color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
}
.result-top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    direction: ltr;
}
.sim-score-badge {
    background: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 0.82rem;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 10px rgba(79, 70, 229, 0.4);
}
.result-doc-title {
    font-size: 1.18rem;
    font-weight: 800;
    color: #ffffff;
    direction: rtl;
    text-align: right;
}
.source-tag {
    display: inline-block;
    background: #182236;
    color: #94a3b8;
    font-size: 0.8rem;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 0.6rem;
    font-weight: 600;
    border: 1px solid #28354f;
}
.snippet-content {
    background: #090d16;
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.75;
    padding: 0.95rem 1.2rem;
    border-radius: 14px;
    border-right: 4px solid #6366f1;
    margin-top: 0.6rem;
}

/* Course Pill Cards */
.course-item-card {
    background: #0f1523;
    border: 1px solid #1e293d;
    border-radius: 16px;
    padding: 1.15rem 1.4rem;
    margin-bottom: 0.85rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    direction: rtl;
    transition: all 0.2s ease;
}
.course-item-card:hover {
    border-color: #6366f1;
    transform: translateX(-4px);
    background: #131b2e;
}
.c-code-pill {
    background: rgba(99, 102, 241, 0.15);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.4);
    font-weight: 800;
    font-size: 0.95rem;
    padding: 4px 12px;
    border-radius: 10px;
    display: inline-block;
}
.c-title-ar-txt {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
    margin-right: 12px;
}
.c-title-en-txt {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-right: 8px;
}
.c-details-sub {
    font-size: 0.83rem;
    color: #64748b;
    margin-top: 5px;
}
.status-pill-ok {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 5px 14px;
    border-radius: 30px;
    font-size: 0.82rem;
    font-weight: 700;
    white-space: nowrap;
}
.status-pill-fail {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 5px 14px;
    border-radius: 30px;
    font-size: 0.82rem;
    font-weight: 700;
    white-space: nowrap;
}

/* FAQ Expanders Styling */
[data-testid="stExpander"] {
    background: #0f1523 !important;
    border: 1px solid #1f293d !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    direction: rtl !important;
    text-align: right !important;
}
[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    font-size: 1rem !important;
    color: #f1f5f9 !important;
}

/* Form Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background: #0d121f !important;
    color: #ffffff !important;
    border: 1px solid #243048 !important;
    border-radius: 12px !important;
    font-size: 0.95rem !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
}
.stSelectbox>div>div {
    background: #0d121f !important;
    color: #ffffff !important;
    border: 1px solid #243048 !important;
    border-radius: 12px !important;
}

/* Primary Buttons */
.stButton>button {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
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

# Ensure in-memory FAQ persistence in Session State across in-app interactions
if "faqs" not in st.session_state:
    st.session_state["faqs"] = fm.load_faqs()


# Sidebar Configuration
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0 10px 0; border-bottom: 1px solid #1f293d; margin-bottom: 15px;">
        <div style="font-size: 2.8rem; margin-bottom: 5px;">🤖</div>
        <div style="font-size: 1.3rem; font-weight: 800; color: #ffffff;">Smart Student Guide</div>
        <div style="font-size: 0.83rem; color: #94a3b8;">كلية الذكاء الاصطناعي - كفر الشيخ</div>
        <div style="margin-top: 10px;">
            <span class="pill-team-flair">❤️ فريق: قصة عشق</span>
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
            "المقررات المجتازة بنجاح:",
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
<div class="hero-container">
    <div class="hero-title-main">
        🎓 دليل الطالب الأكاديمي الذكي (Smart Student Guide)
    </div>
    <div class="hero-sub-text">
        نظام ذكي متكامل للمعلومات واللوائح الأكاديمية والاستدلال — كلية الذكاء الاصطناعي (جامعة كفر الشيخ)
    </div>
    <div class="hero-badges-row">
        <span class="pill-neutral">⚡ Task 1: AI Assignment</span>
        <span class="pill-neutral">📘 لائحة الساعات المعتمدة 2023</span>
        <span class="pill-team-flair">❤️ فريق العمل: قصة عشق</span>
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

    # Metric Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">المستوى الدراسي</div>
            <div class="metric-val-txt">{rep["academic_level"].split()[0]} {rep["academic_level"].split()[1]}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">الساعات المجتازة / 144</div>
            <div class="metric-val-txt">{passed_hrs} <span style="font-size:0.9rem; color:#94a3b8; font-weight:500;">ساعة</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">المعدل التراكمي CGPA</div>
            <div class="metric-val-txt">{cgpa:.2f} <span style="font-size:0.9rem; color:#818cf8; font-weight:500;">/ 4.0</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        limits = rep["credit_limits"]
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">العبء الدراسي المسموح</div>
            <div class="metric-val-txt">{limits['min_hours']} - {limits['max_hours']} <span style="font-size:0.9rem; color:#94a3b8; font-weight:500;">ساعة</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Progress toward graduation
    st.markdown(f"""
    <div style="direction: rtl; text-align: right; margin: 1.4rem 0 0.4rem 0; font-size: 0.88rem; font-weight: 700; color: #94a3b8;">
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
        st.caption("ابحث باللغة العربية أو الإنجليزية في لوائح الكلية الأكاديمية، توصيف المقررات، بيانات أعضاء هيئة التدريس، ومواقع القاعات والمعامل.")

        col_search, col_k = st.columns([5, 1])
        with col_search:
            query = st.text_input(
                "اكتب استفسارك هنا:",
                value="مشروع التخرج وساعاته",
                placeholder="أمثلة: شروط التسجيل، الإنذار الأكاديمي، مكتب العميد، معمل الروبوتات، Deep learning..."
            )
        with col_k:
            top_k = st.selectbox("عدد النتائج:", [3, 5, 8], index=0)

        if query.strip():
            results = student_service.search_academic_information(query, top_k=top_k)
            if not results:
                st.warning("لم يتم العثور على وثائق مطابقة لاستفسارك.")
            else:
                st.markdown(f"**تم العثور على ({len(results)}) نتائج مرتبة حسب درجة التطابق (Cosine Similarity):**")
                for r in results:
                    score_pct = round(r['score'] * 100, 1)
                    st.markdown(f"""
                    <div class="result-card-box">
                        <div class="result-top-bar">
                            <span class="sim-score-badge">Cosine Sim: {r['score']:.4f} ({score_pct}%)</span>
                            <span class="result-doc-title">📄 {r['title']}</span>
                        </div>
                        <span class="source-tag">📁 المصدر: {r['source_file']}</span>
                        <div class="snippet-content">{r['snippet']}</div>
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
                <div class="course-item-card">
                    <div>
                        <span class="c-code-pill">{c['course_code']}</span>
                        <span class="c-title-ar-txt">{c['title_ar']}</span>
                        <span class="c-title-en-txt">({c['title_en']})</span>
                        <div class="c-details-sub">
                            الساعات: <b>{c['credit_hours']}</b> | المستوى: <b>{c['level']}</b> | القسم: <b>{c['department']}</b> | النوع: <b>{c['course_type']}</b>
                        </div>
                    </div>
                    <div>
                        <span class="status-pill-ok">✓ مستوفى: {prereqs}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander(f"🔒 عرض المقررات المقفلة لعدم استيفاء المتطلبات ({len(locked)} مقرر)"):
            for c in locked:
                missing = ", ".join(c["missing_prerequisites"])
                st.markdown(f"""
                <div class="course-item-card" style="opacity: 0.8; border-color: #451a1a;">
                    <div>
                        <span class="c-code-pill" style="background:#3b1111; color:#f87171; border-color:#7f1d1d;">{c['course_code']}</span>
                        <span class="c-title-ar-txt">{c['title_ar']}</span>
                        <span class="c-title-en-txt">({c['title_en']})</span>
                        <div class="c-details-sub">المستوى: {c['level']} | الساعات: {c['credit_hours']}</div>
                    </div>
                    <div>
                        <span class="status-pill-fail">⚠️ يتطلب: {missing}</span>
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
                <div style="background:#064e3b; border:1px solid #059669; border-radius:14px; padding:16px; margin: 15px 0; direction: rtl; text-align: right;">
                    <h4 style="color:#6ee7b7; margin:0 0 6px 0;">✅ مؤهل لتسجيل المقرر بنجاح!</h4>
                    <p style="color:#d1fae5; margin:0;">{res.get('reason')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#450a0a; border:1px solid #b91c1c; border-radius:14px; padding:16px; margin: 15px 0; direction: rtl; text-align: right;">
                    <h4 style="color:#fca5a5; margin:0 0 6px 0;">❌ غير مؤهل للتسجيل حالياً</h4>
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
                        <div class="result-card-box" style="margin-bottom: 8px; padding: 0.9rem 1.2rem; border-right: 4px solid #8b5cf6;">
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
        # Load from session state so freshly added questions appear immediately!
        faqs_list = st.session_state.get("faqs", fm.load_faqs())
        st.caption(f"عدد الأسئلة المسجلة: ({len(faqs_list)}) سؤالاً.")
        for f in faqs_list:
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
        <div class="metric-box">
            <div class="metric-label-txt">إجمالي المقررات</div>
            <div class="metric-val-txt">{stats['total_courses']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">المقاطع المفهرسة (IR)</div>
            <div class="metric-val-txt">{stats['indexed_passages']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        faqs_count = len(st.session_state.get("faqs", fm.load_faqs()))
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">الأسئلة الشائعة</div>
            <div class="metric-val-txt">{faqs_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label-txt">الاستعلامات المسجلة</div>
            <div class="metric-val-txt">{stats['logged_queries_count']}</div>
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
        st.subheader("💡 إدارة وإضافة الأسئلة الشائعة")
        with st.form("faq_form_admin"):
            fq = st.text_input("نص السؤال بالعربية:")
            fq_en = st.text_input("السؤال بالإنجليزية (اختياري):")
            fa = st.text_area("الإجابة الرسمية:")
            faq_sub = st.form_submit_button("إضافة وحفظ السؤال")
            if faq_sub and fq and fa:
                new_f = admin_service.add_faq(fq, fa, fq_en)
                # Ensure Session State is updated immediately
                if "faqs" in st.session_state:
                    st.session_state["faqs"].append(new_f)
                # Re-index into IR search
                ir_index.add_document(
                    doc_id=f"faq_{new_f['id']}",
                    title=f"سؤال شائع: {new_f['question']}",
                    text=f"{new_f['question']}\n{new_f.get('question_en', '')}\nالإجابة: {new_f['answer']}",
                    source_file="faqs.json"
                )
                ir_index.build()
                st.success(f"✅ تمت إضافة السؤال بنجاح برقم {new_f['id']} وأصبح متاحاً فوراً في البحث وقائمة الأسئلة!")

        st.markdown("---")
        st.markdown("#### 📥 حفظ الأسئلة بشكل دائم (Export):")
        st.caption("إذا أردت تنزيل ملف الأسئلة وحفظه بشكل دائم في مجلد مشروعك:")
        current_faqs_json = json.dumps(st.session_state.get("faqs", fm.load_faqs()), ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 تحميل ملف faqs.json المحدث",
            data=current_faqs_json,
            file_name="faqs.json",
            mime="application/json"
        )

    with atab5:
        st.subheader("📜 سجل الاستعلامات والعمليات الفعلي (queries.log)")
        logs = admin_service.view_logs(50)
        st.text_area("أحدث السجلات:", value="\n".join(logs), height=400)

# Footer
st.markdown("""
<div style="direction: rtl; text-align: center; color: #64748b; font-size: 0.88rem; padding: 30px 0 15px 0; border-top: 1px solid #1f293d; margin-top: 40px;">
    تم التطوير وتصميم النظام بواسطة فريق <b style="color: #f43f5e;">قصة عشق ❤️</b> — مقرر الذكاء الاصطناعي (جامعة كفر الشيخ) 2026
</div>
""", unsafe_allow_html=True)
