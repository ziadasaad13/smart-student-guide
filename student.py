"""Student interface."""
import config
import file_manager as fm
from utils import ask_float, ask_int, ask_str, ask_yes_no, parse_codes

SEM_CHOICES = {"1": "First", "2": "Second", "3": "Summer"}
SEM_NAME = {"First": "الفصل الأول", "Second": "الفصل الثاني", "Summer": "الصيفي"}


def _pick_semester():
    print("Semester: 1) First (الأول)  2) Second (الثاني)  3) Summer (صيفي)")
    return SEM_CHOICES[str(ask_int("Choose", 1, 3, 1))]


def enter_data(ctx, existing=None):
    """Create/update the student record (personal data entry)."""
    s = dict(existing or {})
    s["id"] = ask_str("Student ID (رقم الطالب)", s.get("id"))
    old = fm.get_student(s["id"])
    if old and not existing:
        print(f"Found saved record for {old['name']} - press Enter to keep values.")
        s = dict(old)
    s["name"] = ask_str("Name (الاسم)", s.get("name"))
    s["cgpa"] = ask_float("CGPA 0-4 (المعدل التراكمي)", 0, 4, s.get("cgpa", 0.0))
    s["first_semester"] = ask_yes_no("Is this your FIRST semester in college? (فصلك الأول؟)", s.get("first_semester", False))
    s["science_stream"] = ask_yes_no("Thanaweya 'ilmi 'oloum (علمي علوم)?", s.get("science_stream", False))
    cur = ",".join(s.get("completed", []))
    while True:
        codes = parse_codes(ask_str("Passed courses, comma separated (المقررات التي نجحت فيها)", cur, True))
        bad = [c for c in codes if c not in ctx.kb.courses]
        if bad:
            print("  ! unknown course codes:", ", ".join(bad))
            continue
        s["completed"] = list(dict.fromkeys(codes))
        break
    s["semesters_studied"] = ask_int("Regular semesters studied so far (عدد الفصول)", 0, 30, s.get("semesters_studied", 0))
    s["consecutive_warnings"] = ask_int("Consecutive academic warnings before this semester", 0, 10, s.get("consecutive_warnings", 0))
    s["total_warnings"] = ask_int("Total academic warnings before this semester", 0, 10, s.get("total_warnings", 0))
    s["training_done"] = ask_yes_no("Summer training completed? (التدريب الميداني)", s.get("training_done", False))
    s["ever_failed"] = ask_yes_no("Ever failed/deprived in a course? (رسبت أو حرمت من قبل؟)", s.get("ever_failed", False))
    fm.save_student(s)
    fm.log_event(s["id"], "STUDENT_DATA", "save", s["name"])
    print("Saved / تم الحفظ.")
    return s


def print_answer(ans):
    if ans["type"] == "faq":
        print(f"\n[FAQ match {ans['score']:.2f}] {ans['question']}")
        print("  الإجابة:", ans["answer"], f"({ans['source']})")
    elif ans["results"]:
        print("\nأقرب المستندات:")
        for i, r in enumerate(ans["results"], 1):
            print(f"{i}. {r['title']}  [{r['doc']}]  score={r['score']:.2f}")
            print("   ", r["snippet"])
    else:
        print("لم أجد نتائج. جرّب كلمات أخرى (مثال: الحضور، المعدل، التسجيل).")


def ask_question(ctx, student):
    q = ask_str("Your question (سؤالك)")
    ans = ctx.answer_question(q)
    print_answer(ans)
    summary = ans["question"] if ans["type"] == "faq" else (
        f"top={ans['results'][0]['doc']} ({ans['results'][0]['score']:.2f})" if ans["results"] else "no results")
    fm.log_event(student["id"], "QUESTION", q, summary)


def show_eligible(ctx, student):
    sem = _pick_semester()
    kb = ctx.kb
    api = None if sem == "Summer" else sem
    elig = kb.eligible_courses(student, api)
    print(f"\nمستواك: {kb.level_of(student)} | ساعات مجتازة: {kb.passed_credits(student)} | "
          f"أقصى ساعات للتسجيل: {kb.max_credits(student, summer=(sem == 'Summer'))}")
    print(f"\nالمقررات المتاحة لك ({SEM_NAME[sem]}):")
    for c in elig:
        cc = kb.courses[c]
        print(f"  ✓ {kb.label(c)} - {cc['credits']} ساعات - {'إجباري' if cc['status'] == 'Core' else 'اختياري'}")
    if ask_yes_no("Show why other courses are NOT available? (اعرض أسباب عدم الأهلية)", False):
        for c, (ok, reasons) in kb.explain_all(student, api).items():
            if not ok and "اجتيازه من قبل" not in reasons[0] and int(kb.courses[c]["level"]) <= kb.level_of(student) + 1:
                print(f"  ✗ {kb.label(c)}: {' - '.join(reasons)}")
    plan, total, mx = kb.suggest_plan(student, sem)
    print(f"\nخطة مقترحة ({total}/{mx} ساعة): " + ", ".join(plan))
    fm.log_event(student["id"], "ELIGIBLE_COURSES", SEM_NAME[sem], ",".join(elig))


def check_plan(ctx, student):
    sem = _pick_semester()
    codes = parse_codes(ask_str("Planned courses (المقررات التي تنوي تسجيلها)"))
    res = ctx.kb.validate_plan(student, codes, sem)
    print(f"\nمجموع الساعات: {res['total']} (الحد الأدنى {res['min']} / الأقصى {res['max']})")
    if res["ok"]:
        print("✓ الخطة سليمة حسب اللائحة.")
    else:
        for p in res["problems"]:
            print("  ✗", p)
    fm.log_event(student["id"], "CHECK_PLAN", ",".join(codes), "OK" if res["ok"] else f"{len(res['problems'])} problems")


def course_info(ctx, student):
    code = ask_str("Course code (كود المقرر)").upper()
    kb = ctx.kb
    if code not in kb.courses:
        print("المقرر غير موجود.")
        return
    c = kb.courses[code]
    print(f"\n{kb.label(code)} - {c['name_en']}")
    print(f"  الساعات: {c['credits']} | المستوى: {c['level']} | الفصل: {'الأول' if c['semester'] == 'First' else 'الثاني'} | "
          f"{'إجباري' if c['status'] == 'Core' else 'اختياري'} | نوع التقييم: {c['type']}")
    print("  المتطلبات المباشرة:", "، ".join(kb.label(p) for p in kb.prereq[code]) or "لا يوجد")
    chain = kb.full_prereq_chain(code)
    if chain:
        print("  كل المتطلبات (مباشرة وغير مباشرة):", ", ".join(chain))
    deps = kb.dependents(code)
    if deps:
        print("  يفتح لك مقررات:", ", ".join(deps))
    print("  المحاضر:", c["instructor"] or "لم يُحدد بعد")
    assess = ctx.rules.get("assessment", {}).get(c["type"])
    if assess:
        print("  توزيع الدرجات:", " | ".join(f"{k}: {v}" for k, v in assess.items()))
    rows = [r for r in ctx.schedule if r["code"] == code]
    if rows:
        print("  الجدول (الفصل الأول 2026-2027):")
        for r in rows:
            print(f"    {r['day']} {r['start']}-{r['end']} | {'محاضرة' if r['kind'] == 'lecture' else 'معمل'} مجموعة {r['group']} | {r['room']} | {r['instructor']}")
    if c["notes"]:
        print("  ملاحظة:", c["notes"])
    fm.log_event(student["id"], "COURSE_INFO", code, "")


def show_day(ctx, student):
    day = ask_str("Day (اليوم: السبت/الأحد/الاثنين/الثلاثاء/الأربعاء/الخميس)")
    rows = sorted([r for r in ctx.schedule if r["day"] == day], key=lambda r: r["start"])
    if not rows:
        print("لا توجد محاضرات في هذا اليوم.")
    for r in rows:
        print(f"{r['start']}-{r['end']} | {ctx.kb.label(r['code'])} | {'محاضرة' if r['kind'] == 'lecture' else 'معمل'} م{r['group']} | {r['room']} | {r['instructor']}")
    fm.log_event(student["id"], "DAY_SCHEDULE", day, f"{len(rows)} rows")


def academic_status(ctx, student):
    st = ctx.kb.academic_status(student)
    print(f"\nالمستوى: {st['level']} | الساعات المجتازة: {st['passed']} | المتبقي للتخرج: {st['remaining']} | "
          f"CGPA: {st['cgpa']} ({st['general_grade']}) | أقصى تسجيل: {st['max_credits']} ساعة")
    for m in st["messages"]:
        print(" -", m)
    ok, missing = ctx.kb.graduation_check(student)
    print("شروط التخرج:", "مستوفاة ✓" if ok else "غير مستوفاة:")
    for m in missing:
        print("   •", m)
    hok, hr = ctx.kb.honors_check(student)
    print("مرتبة الشرف:", "مؤهل ✓" if hok else "غير مؤهل: " + " - ".join(hr))
    fm.log_event(student["id"], "ACADEMIC_STATUS", "", f"level={st['level']} cgpa={st['cgpa']}")


def gpa_calculator(ctx, student):
    entries = []
    print("Enter each course: credits and final percent. Empty credits to finish.")
    while True:
        raw = ask_str("Credit hours (الساعات)", "", True)
        if not raw:
            break
        try:
            cr = int(raw)
        except ValueError:
            continue
        pct = ask_float("Total percent (النسبة الكلية)", 0, 100)
        fin = ask_float("Final written exam percent (نسبة امتحان النهاية)", 0, 100)
        res, letter, pts = ctx.kb.course_result(pct, fin)
        print(f"   -> {res} | {letter} | {pts}")
        entries.append((cr, pts))
    if entries:
        print("GPA:", ctx.kb.calc_gpa(entries))
        fm.log_event(student["id"], "GPA_CALC", f"{len(entries)} courses", str(ctx.kb.calc_gpa(entries)))


def attendance(ctx, student):
    total = ask_int("Total lectures+labs so far (إجمالي المحاضرات)", 1, 200)
    missed = ask_int("Missed (عدد مرات الغياب)", 0, total)
    pct = missed * 100 / total
    _, msg = ctx.kb.attendance_status(pct)
    print(f"نسبة الغياب {pct:.1f}% -> {msg}")
    fm.log_event(student["id"], "ATTENDANCE", f"{missed}/{total}", msg)


def student_menu(ctx):
    student = enter_data(ctx)
    while True:
        print("""
=== Student (الطالب) ===
1. Update my data (تحديث بياناتي)
2. Ask a question (اسأل سؤال)
3. Which courses can I register? (المقررات المتاحة لي)
4. Check my planned registration (راجع خطة تسجيلي)
5. Course info (معلومات مقرر)
6. Timetable by day (جدول اليوم)
7. My academic status & graduation (وضعي الأكاديمي)
8. GPA calculator (حاسبة المعدل)
9. Attendance checker (حاسبة الغياب)
0. Back""")
        c = ask_str("Choose", "0")
        actions = {"2": ask_question, "3": show_eligible, "4": check_plan, "5": course_info, "6": show_day,
                   "7": academic_status, "8": gpa_calculator, "9": attendance}
        if c == "0":
            return
        if c == "1":
            student = enter_data(ctx, student)
        elif c in actions:
            actions[c](ctx, student)
        else:
            print("Invalid choice.")
