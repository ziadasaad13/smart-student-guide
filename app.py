"""Streamlit interface (Arabic / RTL) for the Smart Student Guide.
Run:  streamlit run app.py"""
import os
import re

import pandas as pd
import streamlit as st

import config
import file_manager as fm
from context import Context

st.set_page_config(page_title="دليل الطالب الذكي", page_icon="🎓", layout="wide")

# ---------------------------------------------------------------- style (RTL + Arabic font)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
html, body, .stApp, [data-testid="stSidebar"], .stMarkdown, label, input, textarea, button, p, h1, h2, h3, h4 {
  font-family: 'Cairo', 'Tahoma', sans-serif !important; }
.stApp, [data-testid="stSidebar"] { direction: rtl; text-align: right; }
[data-testid="stSidebar"] { border-left: 1px solid rgba(128,128,128,.25); }
.stTabs [data-baseweb="tab-list"] { gap: 6px; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 8px 14px; }
div[data-testid="stMetric"] { background: rgba(99,102,241,.08); border: 1px solid rgba(99,102,241,.25);
  padding: 12px 16px; border-radius: 14px; }
.card { border: 1px solid rgba(128,128,128,.3); border-radius: 14px; padding: 14px 18px; margin: 8px 0;
  background: rgba(128,128,128,.06); }
.card .src { opacity: .65; font-size: .85em; }
.badge { display:inline-block; padding: 2px 10px; border-radius: 999px; font-size:.8em;
  background: rgba(99,102,241,.18); margin-left: 6px; }
.hero { background: linear-gradient(135deg,#4f46e5,#7c3aed); color: #fff; padding: 22px 26px; border-radius: 18px; margin-bottom: 14px; }
.hero h1 { color:#fff; margin:0; font-size: 1.7em; } .hero p { margin:4px 0 0; opacity:.9; }
input, textarea { direction: auto; }
</style>
""", unsafe_allow_html=True)

SEM = {"الفصل الأول": "First", "الفصل الثاني": "Second", "الصيفي": "Summer"}
SEM_AR = {"First": "الأول", "Second": "الثاني"}
DAYS = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
CODE_RE = re.compile(r"^[A-Z]{2}\d{3}$")


@st.cache_resource
def get_ctx():
    return Context()


ctx = get_ctx()
kb = ctx.kb


def flash(msg):
    st.session_state["_flash"] = msg
    st.rerun()


def show_flash():
    if "_flash" in st.session_state:
        st.success(st.session_state.pop("_flash"))


# ---------------------------------------------------------------- hero
st.markdown("""<div class="hero"><h1>🎓 دليل الطالب الذكي</h1>
<p>كلية الذكاء الاصطناعي – جامعة كفر الشيخ | لائحة 2023</p></div>""", unsafe_allow_html=True)

mode = st.sidebar.radio("الواجهة", ["👨‍🎓 الطالب", "🛠️ الأدمن"], horizontal=True)

# =================================================================== STUDENT
def student_profile_sidebar():
    """Select / create / edit the current student. Returns the student dict (or None)."""
    if "_select_next" in st.session_state:
        st.session_state["sel"] = st.session_state.pop("_select_next")
    students = fm.load_students()
    names = {s["id"]: s["name"] for s in students}
    NEW = "➕ طالب جديد"
    choice = st.sidebar.selectbox("اختر الطالب", [NEW] + list(names), key="sel",
                                  format_func=lambda x: x if x == NEW else f"{x} - {names[x]}")
    cur = fm.get_student(choice) if choice != NEW else None
    d = cur or {}
    with st.sidebar.expander("📝 بياناتي / تعديل", expanded=cur is None):
        with st.form(f"profile_{choice}"):
            sid = st.text_input("رقم الطالب", d.get("id", ""), disabled=cur is not None)
            name = st.text_input("الاسم", d.get("name", ""))
            cgpa = st.number_input("المعدل التراكمي (CGPA)", 0.0, 4.0, float(d.get("cgpa", 0.0)), 0.01, format="%.2f")
            first = st.checkbox("هذا فصلي الأول بالكلية", d.get("first_semester", False))
            sci = st.checkbox("ثانوية عامة علمي علوم", d.get("science_stream", False))
            codes = sorted(kb.courses)
            done = st.multiselect("المقررات التي نجحت فيها", codes,
                                  [c for c in d.get("completed", []) if c in kb.courses],
                                  format_func=lambda c: kb.label(c))
            sems = st.number_input("عدد الفصول الدراسية السابقة", 0, 30, int(d.get("semesters_studied", 0)))
            cw = st.number_input("إنذارات أكاديمية متتالية سابقة", 0, 10, int(d.get("consecutive_warnings", 0)))
            tw = st.number_input("إجمالي الإنذارات الأكاديمية السابقة", 0, 10, int(d.get("total_warnings", 0)))
            tr = st.checkbox("أتممت التدريب الميداني", d.get("training_done", False))
            ff = st.checkbox("سبق لي الرسوب أو الحرمان في مقرر", d.get("ever_failed", False))
            if st.form_submit_button("💾 حفظ", use_container_width=True):
                sid = (cur["id"] if cur else sid.strip())
                if not sid or not name.strip():
                    st.error("رقم الطالب والاسم مطلوبان")
                else:
                    fm.save_student({"id": sid, "name": name.strip(), "cgpa": cgpa, "first_semester": first,
                                     "science_stream": sci, "completed": done, "semesters_studied": int(sems),
                                     "consecutive_warnings": int(cw), "total_warnings": int(tw),
                                     "training_done": tr, "ever_failed": ff})
                    fm.log_event(sid, "STUDENT_DATA", "save", name)
                    st.session_state["_select_next"] = sid
                    flash("تم حفظ بياناتك ✓")
    return cur


def tab_ask(student):
    st.subheader("اسأل عن اللائحة")
    with st.form("ask"):
        q = st.text_input("اكتب سؤالك", placeholder="مثال: نسبة الحضور المطلوبة إيه؟")
        go = st.form_submit_button("🔍 ابحث", use_container_width=True)
    if go and q.strip():
        ans = ctx.answer_question(q)
        if ans["type"] == "faq":
            st.markdown(f"""<div class="card"><b>{ans['question']}</b><br>{ans['answer']}
            <div class="src">المصدر: {ans['source']} · درجة التطابق {ans['score']:.2f}</div></div>""", unsafe_allow_html=True)
            fm.log_event(student["id"], "QUESTION", q, ans["question"])
        elif ans["results"]:
            st.caption("لا توجد إجابة جاهزة، هذه أقرب المستندات:")
            for r in ans["results"]:
                st.markdown(f"""<div class="card"><b>{r['title']}</b> <span class="badge">{r['score']:.2f}</span><br>
                {r['snippet']}<div class="src">{r['doc']}</div></div>""", unsafe_allow_html=True)
            fm.log_event(student["id"], "QUESTION", q, f"top={ans['results'][0]['doc']}")
        else:
            st.warning("لم أجد نتائج، جرّب كلمات أخرى (الحضور، المعدل، التسجيل...)")
            fm.log_event(student["id"], "QUESTION", q, "no results")
    with st.expander("أمثلة لأسئلة"):
        st.write("• متى أنتقل للمستوى الثالث؟  • كيف أحسب المعدل؟  • ما الحد الأقصى للساعات؟  • شروط مرتبة الشرف")


def tab_eligible(student):
    st.subheader("المقررات المتاحة لي")
    sem_label = st.radio("الفصل", list(SEM), horizontal=True, key="el_sem")
    sem = SEM[sem_label]
    api = None if sem == "Summer" else sem
    c1, c2, c3 = st.columns(3)
    c1.metric("مستواي", kb.level_of(student))
    c2.metric("ساعات مجتازة", kb.passed_credits(student))
    c3.metric("أقصى ساعات للتسجيل", kb.max_credits(student, summer=(sem == "Summer")))
    elig = kb.eligible_courses(student, api)
    st.markdown(f"**✅ {len(elig)} مقرر متاح**")
    st.dataframe(pd.DataFrame([{"الكود": c, "المقرر": kb.courses[c]["name_ar"], "الساعات": kb.credits(c),
                                "المستوى": kb.courses[c]["level"],
                                "النوع": "إجباري" if kb.courses[c]["status"] == "Core" else "اختياري"} for c in elig]),
                 use_container_width=True, hide_index=True)
    plan, total, mx = kb.suggest_plan(student, sem)
    st.info(f"**خطة مقترحة ({total}/{mx} ساعة):** " + "، ".join(kb.label(c) for c in plan))
    with st.expander("❌ لماذا لا أستطيع تسجيل باقي المقررات؟"):
        rows = [{"المقرر": kb.label(c), "السبب": " - ".join(r)} for c, (ok, r) in kb.explain_all(student, api).items()
                if not ok and "اجتيازه من قبل" not in r[0] and int(kb.courses[c]["level"]) <= kb.level_of(student) + 1]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    fm.log_event(student["id"], "ELIGIBLE_COURSES", sem_label, ",".join(elig))


def tab_plan(student):
    st.subheader("راجع خطة تسجيلي")
    sem_label = st.radio("الفصل", list(SEM), horizontal=True, key="pl_sem")
    picks = st.multiselect("المقررات التي أنوي تسجيلها", sorted(kb.courses), format_func=lambda c: kb.label(c))
    if picks:
        res = kb.validate_plan(student, picks, SEM[sem_label])
        a, b, c = st.columns(3)
        a.metric("مجموع الساعات", res["total"])
        b.metric("الحد الأدنى", res["min"])
        c.metric("الحد الأقصى", res["max"])
        if res["ok"]:
            st.success("✓ الخطة سليمة حسب اللائحة")
        else:
            for p in res["problems"]:
                st.error(p)
        fm.log_event(student["id"], "CHECK_PLAN", ",".join(picks), "OK" if res["ok"] else f"{len(res['problems'])} problems")


def tab_course(student):
    st.subheader("معلومات مقرر")
    code = st.selectbox("المقرر", sorted(kb.courses), format_func=lambda c: kb.label(c))
    c = kb.courses[code]
    st.markdown(f"### {c['name_ar']}  \n*{c['name_en']}*")
    a, b, d, e = st.columns(4)
    a.metric("الساعات", c["credits"]); b.metric("المستوى", c["level"])
    d.metric("الفصل", SEM_AR[c["semester"]]); e.metric("النوع", "إجباري" if c["status"] == "Core" else "اختياري")
    st.write("**المتطلبات المباشرة:**", "، ".join(kb.label(p) for p in kb.prereq[code]) or "لا يوجد")
    chain = kb.full_prereq_chain(code)
    if chain:
        st.write("**كل المتطلبات (مباشرة وغير مباشرة):**", "، ".join(chain))
    if kb.dependents(code):
        st.write("**يفتح لك مقررات:**", "، ".join(kb.dependents(code)))
    st.write("**المحاضر:**", c["instructor"] or "لم يُحدد بعد")
    ok, why = kb.check(student, code)
    (st.success("✓ يمكنك تسجيله حاليا") if ok else st.warning("لا يمكنك تسجيله: " + " - ".join(why)))
    assess = ctx.rules.get("assessment", {}).get(c["type"])
    if assess:
        names = {"final": "امتحان نهائي", "coursework": "أعمال فصلية", "practical": "عملي", "oral": "شفوي",
                 "oral_and_documents": "شفوي ومستندات"}
        st.write("**توزيع الدرجات:** " + " | ".join(f"{names.get(k, k)}: {v}" for k, v in assess.items()))
    rows = [r for r in ctx.schedule if r["code"] == code]
    if rows:
        st.write("**الجدول (الفصل الأول 2026-2027):**")
        st.dataframe(pd.DataFrame([{"اليوم": r["day"], "من": r["start"], "إلى": r["end"],
                                    "النوع": "محاضرة" if r["kind"] == "lecture" else "معمل", "المجموعة": r["group"],
                                    "المكان": r["room"], "المحاضر": r["instructor"]} for r in rows]),
                     use_container_width=True, hide_index=True)
    if c["notes"]:
        st.caption("ملاحظة: " + c["notes"])
    doc = ctx.docs.get(f"course_{code}.txt")
    if doc:
        with st.expander("وصف المقرر"):
            st.write(doc.split("الوصف:", 1)[-1])
    fm.log_event(student["id"], "COURSE_INFO", code, "")


def tab_schedule(student):
    st.subheader("جدول المستوى الثاني – الفصل الأول 2026-2027")
    day = st.radio("اليوم", DAYS, horizontal=True)
    rows = sorted([r for r in ctx.schedule if r["day"] == day], key=lambda r: r["start"])
    if rows:
        st.dataframe(pd.DataFrame([{"الوقت": f"{r['start']} - {r['end']}", "المقرر": kb.label(r["code"]),
                                    "النوع": "محاضرة" if r["kind"] == "lecture" else "معمل", "المجموعة": r["group"],
                                    "المكان": r["room"], "المحاضر": r["instructor"]} for r in rows]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد محاضرات في هذا اليوم.")


def tab_status(student):
    st.subheader("وضعي الأكاديمي")
    st_ = kb.academic_status(student)
    a, b, c, d = st.columns(4)
    a.metric("المستوى", st_["level"]); b.metric("الساعات المجتازة", st_["passed"])
    c.metric("المتبقي للتخرج", st_["remaining"]); d.metric("CGPA", f"{st_['cgpa']} ({st_['general_grade']})")
    total = ctx.rules["graduation_credits"]
    st.progress(min(1.0, st_["passed"] / total), text=f"{st_['passed']} / {total} ساعة")
    for m in st_["messages"]:
        (st.error if st_["dismissal_risk"] else st.warning if st_["warning"] else st.success)(m)
    ok, missing = kb.graduation_check(student)
    st.markdown("#### 🎓 شروط التخرج")
    if ok:
        st.success("مستوفاة ✓")
    for m in missing:
        st.write("• " + m)
    hok, hr = kb.honors_check(student)
    st.markdown("#### 🏅 مرتبة الشرف")
    (st.success("مؤهل ✓") if hok else st.info("غير مؤهل: " + " - ".join(hr)))
    fm.log_event(student["id"], "ACADEMIC_STATUS", "", f"level={st_['level']} cgpa={st_['cgpa']}")


def tab_calc(student):
    st.subheader("حاسبة المعدل")
    st.caption("أدخل كل مقرر: الساعات، النسبة الكلية، ونسبة امتحان نهاية الفصل (لتطبيق قاعدة الـ 30%).")
    df = st.data_editor(pd.DataFrame({"الساعات": [3, 3], "النسبة الكلية %": [85.0, 70.0],
                                      "نسبة امتحان النهاية %": [50.0, 20.0]}),
                        num_rows="dynamic", use_container_width=True, key="gpa_tbl")
    if st.button("احسب", type="primary"):
        out, entries = [], []
        for _, r in df.dropna().iterrows():
            res, letter, pts = kb.course_result(float(r.iloc[1]), float(r.iloc[2]))
            out.append({"الساعات": int(r.iloc[0]), "النتيجة": res, "التقدير": letter, "النقاط": pts})
            entries.append((int(r.iloc[0]), pts))
        if entries:
            st.dataframe(pd.DataFrame(out), use_container_width=True, hide_index=True)
            gpa = kb.calc_gpa(entries)
            st.metric("المعدل الفصلي", gpa)
            fm.log_event(student["id"], "GPA_CALC", f"{len(entries)} courses", str(gpa))


def tab_attendance(student):
    st.subheader("حاسبة الغياب")
    total = st.number_input("إجمالي المحاضرات والمعامل حتى الآن", 1, 200, 20)
    missed = st.number_input("عدد مرات الغياب", 0, int(total), 0)
    pct = missed * 100 / total
    state, msg = kb.attendance_status(pct)
    st.metric("نسبة الغياب", f"{pct:.1f}%")
    {"ok": st.success, "warning": st.warning, "deprived": st.error}[state](msg)


def student_page():
    student = student_profile_sidebar()
    show_flash()
    if not student:
        st.info("👈 اختر طالبا من القائمة الجانبية (مثلا S001) أو أدخل بياناتك كطالب جديد للبدء.")
        return
    st.markdown(f"### أهلا {student['name']} 👋")
    tabs = st.tabs(["💬 اسأل", "📚 المواد المتاحة", "✅ خطتي", "🔎 مقرر", "🗓️ الجدول", "🎓 وضعي", "🧮 المعدل", "📅 الغياب"])
    for t, fn in zip(tabs, [tab_ask, tab_eligible, tab_plan, tab_course, tab_schedule, tab_status, tab_calc, tab_attendance]):
        with t:
            fn(student)


# =================================================================== ADMIN
def course_form(code=None):
    editing = code is not None
    c = dict(kb.courses[code]) if editing else {}
    with st.form(f"course_{code}"):
        a, b = st.columns(2)
        ncode = a.text_input("الكود (مثال BC231)", c.get("code", ""), disabled=editing).upper().strip()
        ar = b.text_input("الاسم بالعربي", c.get("name_ar", ""))
        en = a.text_input("الاسم بالإنجليزية", c.get("name_en", ""))
        cr = b.number_input("الساعات المعتمدة", 0, 6, int(c.get("credits") or 3))
        lv = a.selectbox("المستوى", [1, 2, 3, 4], int(c.get("level") or 1) - 1)
        sm = b.selectbox("الفصل", ["First", "Second"], 0 if c.get("semester", "First") == "First" else 1,
                         format_func=lambda x: SEM_AR[x])
        stt = a.selectbox("النوع", ["Core", "Elective"], 0 if c.get("status", "Core") == "Core" else 1,
                          format_func=lambda x: "إجباري" if x == "Core" else "اختياري")
        ty = b.selectbox("نوع التقييم", ["P", "T", "H", "G"], ["P", "T", "H", "G"].index(c.get("type", "P")))
        pres = st.multiselect("المتطلبات السابقة", [x for x in sorted(kb.courses) if x != code],
                              [p for p in kb.prereq.get(code, [])] if editing else [], format_func=lambda x: kb.label(x))
        mp = a.number_input("أقل ساعات مجتازة مطلوبة", 0, 144, int(c.get("min_passed_credits") or 0))
        ins = b.text_input("المحاضر", c.get("instructor", ""))
        notes = st.text_input("ملاحظات", c.get("notes", ""))
        if st.form_submit_button("💾 حفظ المقرر", use_container_width=True):
            final = code if editing else ncode
            err = None
            if not CODE_RE.match(final or ""):
                err = "الكود لازم يكون حرفين + 3 أرقام"
            elif not editing and final in kb.courses:
                err = "الكود موجود بالفعل"
            elif not ar.strip() or not en.strip():
                err = "الاسم العربي والإنجليزي مطلوبان"
            elif any(final in kb.full_prereq_chain(p) for p in pres):
                err = "هذا الاختيار يسبب متطلبات دائرية"
            if err:
                st.error(err)
            else:
                row = {"code": final, "name_ar": ar.strip(), "name_en": en.strip(), "credits": str(cr), "level": str(lv),
                       "semester": sm, "status": stt, "type": ty, "prerequisites": ";".join(pres),
                       "min_passed_credits": str(mp), "instructor": ins, "notes": notes}
                courses = fm.load_courses()
                courses = [row if x["code"] == final else x for x in courses] if editing else courses + [row]
                fm.save_courses(courses)
                if f"course_{final}.txt" not in ctx.docs:
                    names = {x["code"]: x["name_ar"] for x in courses}
                    pl = "، ".join(f"{p} ({names.get(p, '')})" for p in pres) or "لا يوجد"
                    fm.save_document(f"course_{final}.txt",
                                     f"مقرر {final} - {ar} ({en})\nالكود: {final} | الساعات: {cr} | المستوى: {lv} | "
                                     f"الفصل: {SEM_AR[sm]}\nالمتطلب السابق: {pl}\nالوصف: {notes or en}\n")
                fm.log_event("admin", "ADMIN_EDIT_COURSE" if editing else "ADMIN_ADD_COURSE", final, en)
                ctx.reload()
                flash("تم حفظ المقرر وإعادة بناء الفهرس ✓")


def admin_courses():
    df = pd.DataFrame(ctx.courses)
    st.dataframe(df[["code", "name_ar", "name_en", "credits", "level", "semester", "status", "prerequisites"]],
                 use_container_width=True, hide_index=True)
    t1, t2, t3 = st.tabs(["➕ إضافة", "✏️ تعديل", "🗑️ حذف"])
    with t1:
        course_form(None)
    with t2:
        code = st.selectbox("اختر المقرر", sorted(kb.courses), format_func=lambda c: kb.label(c), key="edit_c")
        course_form(code)
    with t3:
        code = st.selectbox("اختر المقرر", sorted(kb.courses), format_func=lambda c: kb.label(c), key="del_c")
        deps = kb.dependents(code)
        if deps:
            st.warning("لا يمكن الحذف: المقرر متطلب سابق لـ " + "، ".join(deps))
        elif st.button("حذف نهائي", type="primary"):
            fm.save_courses([c for c in fm.load_courses() if c["code"] != code])
            fm.delete_document(f"course_{code}.txt")
            fm.log_event("admin", "ADMIN_DELETE_COURSE", code, "")
            ctx.reload()
            flash("تم الحذف ✓")


def admin_docs():
    NEW = "➕ مستند جديد"
    sel = st.selectbox("المستند", [NEW] + sorted(ctx.docs), key="doc_sel")
    name = st.text_input("اسم الملف (بدون .txt)", "" if sel == NEW else sel[:-4], disabled=sel != NEW)
    text = st.text_area("المحتوى (السطر الأول = العنوان)", "" if sel == NEW else ctx.docs[sel], height=300, key=f"doc_{sel}")
    a, b = st.columns(2)
    if a.button("💾 حفظ المستند", type="primary", use_container_width=True):
        fname = re.sub(r"[^\w\-]", "_", name.strip()) if sel == NEW else sel[:-4]
        if not fname or not text.strip():
            st.error("الاسم والمحتوى مطلوبان")
        else:
            fm.save_document(fname, text)
            fm.log_event("admin", "ADMIN_ADD_DOC" if sel == NEW else "ADMIN_EDIT_DOC", fname, f"{len(text)} chars")
            ctx.reload()
            flash("تم الحفظ وإعادة بناء الفهرس ✓")
    if sel != NEW and b.button("🗑️ حذف", use_container_width=True):
        fm.delete_document(sel)
        fm.log_event("admin", "ADMIN_DELETE_DOC", sel, "")
        ctx.reload()
        flash("تم الحذف ✓")
    st.caption(f"الفهرس الحالي: {ctx.doc_engine.stats()}")


def _table_editor(title, rows, fields, saver, action):
    st.caption(title + " — عدّل الجدول مباشرة، أضف صفا من الأسفل، ثم اضغط حفظ.")
    df = pd.DataFrame(rows, columns=fields) if rows else pd.DataFrame(columns=fields)
    edited = st.data_editor(df.fillna(""), num_rows="dynamic", use_container_width=True, key=f"ed_{action}")
    if st.button("💾 حفظ", key=f"sv_{action}", type="primary"):
        saver(edited)
        fm.log_event("admin", action, f"{len(edited)} rows", "")
        ctx.reload()
        flash("تم الحفظ ✓")


def admin_faqs():
    def save(df):
        fm.save_faqs([r for r in df.to_dict("records") if str(r["q"]).strip() and str(r["a"]).strip()])
    _table_editor("الأسئلة الشائعة", ctx.faqs, ["q", "a", "source", "keywords"], save, "ADMIN_EDIT_FAQS")


def admin_people():
    t1, t2 = st.tabs(["الدكاترة والمعيدون", "الجدول الدراسي"])
    with t1:
        _table_editor("هيئة التدريس", ctx.staff, fm.STAFF_FIELDS,
                      lambda df: fm.save_staff([r for r in df.to_dict("records") if str(r["name"]).strip()]), "ADMIN_EDIT_STAFF")
    with t2:
        def save(df):
            rows = [r for r in df.to_dict("records") if r["code"] in kb.courses]
            fm.save_schedule(rows)
        _table_editor("الجدول (الأكواد لازم تكون موجودة)", ctx.schedule, fm.SCHEDULE_FIELDS, save, "ADMIN_EDIT_SCHEDULE")


def admin_rules():
    rules = fm.load_rules()
    simple = {k: v for k, v in rules.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    df = pd.DataFrame({"القاعدة": list(simple), "القيمة": list(simple.values())})
    edited = st.data_editor(df, disabled=["القاعدة"], use_container_width=True, hide_index=True, key="rules_ed")
    if st.button("💾 حفظ القواعد", type="primary"):
        for k, v in zip(edited["القاعدة"], edited["القيمة"]):
            rules[k] = int(v) if float(v).is_integer() else float(v)
        fm.save_rules(rules)
        fm.log_event("admin", "ADMIN_EDIT_RULES", "", "")
        ctx.reload()
        flash("تم حفظ القواعد ✓")


def admin_log():
    if os.path.exists(config.LOG_FILE):
        with open(config.LOG_FILE, encoding="utf-8") as f:
            lines = f.read().splitlines()[-200:][::-1]
        rows = [dict(zip(["الوقت", "المستخدم", "العملية", "الاستعلام", "النتيجة"], [x.strip() for x in l.split("|", 4)]))
                for l in lines]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد سجلات بعد.")


def admin_page():
    if not st.session_state.get("is_admin"):
        with st.form("login"):
            pw = st.text_input("كلمة مرور الأدمن", type="password")
            if st.form_submit_button("دخول"):
                if pw == config.ADMIN_PASSWORD:
                    st.session_state["is_admin"] = True
                    st.rerun()
                else:
                    st.error("كلمة المرور غير صحيحة")
        return
    show_flash()
    if st.sidebar.button("تسجيل خروج الأدمن"):
        st.session_state["is_admin"] = False
        st.rerun()
    tabs = st.tabs(["📚 المقررات", "📄 المستندات", "❓ الأسئلة الشائعة", "👥 الدكاترة والجدول", "⚙️ القواعد", "📜 السجل"])
    for t, fn in zip(tabs, [admin_courses, admin_docs, admin_faqs, admin_people, admin_rules, admin_log]):
        with t:
            fn()


if mode.startswith("👨"):
    student_page()
else:
    admin_page()
