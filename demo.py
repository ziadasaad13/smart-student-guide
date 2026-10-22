"""Non-interactive demo that prints the sample runs used in the report."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from context import Context
import file_manager as fm
from student import print_answer

ctx = Context(); kb = ctx.kb
def head(t): print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)

head("1) Search: 'نسبة الحضور المطلوبة'  (FAQ hit)")
a = ctx.answer_question("نسبة الحضور المطلوبة ايه؟"); print_answer(a)
fm.log_event("S001", "QUESTION", "نسبة الحضور المطلوبة ايه؟", a.get("question", ""))

head("2) Search in documents: 'امتحان عملي ودرجات الأعمال الفصلية'")
a = ctx.answer_question("امتحان عملي ودرجات الأعمال الفصلية"); print_answer(a)
fm.log_event("S001", "QUESTION", "امتحان عملي ودرجات الأعمال الفصلية", "docs")

head("3) Eligible courses - S001 (محمد أحمد, CGPA 2.8, 36 passed hours) - First semester")
s = fm.get_student("S001")
for c in kb.eligible_courses(s, "First"): print("  ✓", kb.label(c))
plan, tot, mx = kb.suggest_plan(s, "First"); print(f"  Suggested plan: {plan}  ({tot}/{mx})")

head("4) Why NOT eligible? (S001)")
for c in ("BC312", "ML311", "GP411", "RB411"):
    ok, r = kb.check(s, c); print(f"  ✗ {kb.label(c)}: {' - '.join(r)}")

head("5) Plan validation: S003 (CGPA 1.7 -> max 15 hours)")
s3 = fm.get_student("S003")
print(" ", kb.validate_plan(s3, ["ML211","BC211","BC212","ES211","RB211","HU211"], "First"))

head("6) Academic status - S003 / S002")
for sid in ("S003", "S002"):
    st = kb.academic_status(fm.get_student(sid)); print(" ", sid, st["level"], st["passed"], st["messages"])

head("7) Prerequisite chain of ES422 + dependents of BC211")
print("  chain:", kb.full_prereq_chain("ES422")); print("  dependents:", kb.dependents("BC211"))

head("8) Timetable - Wednesday")
for r in sorted([r for r in ctx.schedule if r["day"] == "الأربعاء"], key=lambda r: r["start"]):
    print(f"  {r['start']}-{r['end']} | {r['code']} | {r['kind']} group={r['group']} | {r['room']} | {r['instructor']}")

head("9) GPA calculation: (3h, 85%), (2h, 70%, final 20%), (3h, 92%)")
e = []
for cr, p, fin in [(3, 85, 50), (2, 70, 20), (3, 92, 55)]:
    res, l, pts = kb.course_result(p, fin); print(f"  {cr}h {p}% -> {res} {l} {pts}"); e.append((cr, pts))
print("  GPA =", kb.calc_gpa(e))
