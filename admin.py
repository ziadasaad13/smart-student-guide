"""Admin interface: courses, documents, FAQs, staff, schedule, rules."""
import re

import config
import file_manager as fm
from utils import ask_int, ask_str, ask_yes_no, parse_codes, read_multiline

CODE_RE = re.compile(r"^[A-Z]{2}\d{3}$")


def _course_doc_text(c, names):
    pres = "، ".join(f"{p} ({names.get(p, '')})" for p in c["prerequisites"].split(";") if p) or "لا يوجد"
    return (f"مقرر {c['code']} - {c['name_ar']} ({c['name_en']})\n"
            f"الكود: {c['code']} | الساعات المعتمدة: {c['credits']} | المستوى: {c['level']} | "
            f"الفصل: {'الأول' if c['semester'] == 'First' else 'الثاني'} | النوع: {'إجباري' if c['status'] == 'Core' else 'اختياري'}\n"
            f"المتطلب السابق: {pres}\nالوصف: {c.get('notes') or c['name_en']}\n")


def _course_form(ctx, c, editing):
    """Ask for course fields with validation. Returns the dict."""
    if not editing:
        while True:
            code = ask_str("Code e.g. BC231").upper()
            if not CODE_RE.match(code):
                print("  ! code must be 2 letters + 3 digits")
            elif code in ctx.kb.courses:
                print("  ! code already exists")
            else:
                c["code"] = code
                break
    c["name_ar"] = ask_str("Arabic name", c.get("name_ar"))
    c["name_en"] = ask_str("English name", c.get("name_en"))
    c["credits"] = str(ask_int("Credit hours", 0, 6, int(c.get("credits") or 3)))
    c["level"] = str(ask_int("Level 1-4", 1, 4, int(c.get("level") or 1)))
    c["semester"] = ask_str("Semester First/Second", c.get("semester", "First"))
    if c["semester"] not in ("First", "Second"):
        c["semester"] = "First"
    c["status"] = "Elective" if ask_str("Core or Elective", c.get("status", "Core")).lower().startswith("e") else "Core"
    c["type"] = ask_str("Type P/T/H/G", c.get("type", "P")).upper()[:1]
    while True:
        pres = parse_codes(ask_str("Prerequisites (comma separated, empty for none)", c.get("prerequisites", "").replace(";", ","), True))
        bad = [p for p in pres if p not in ctx.kb.courses]
        if c.get("code") in pres:
            print("  ! a course cannot be its own prerequisite")
        elif bad:
            print("  ! unknown prerequisite codes:", ", ".join(bad))
        elif c.get("code") and any(c["code"] in ctx.kb.full_prereq_chain(p) for p in pres):
            print("  ! this would create a circular prerequisite")
        else:
            c["prerequisites"] = ";".join(pres)
            break
    c["min_passed_credits"] = str(ask_int("Minimum passed credits required (0 for none)", 0, 144, int(c.get("min_passed_credits") or 0)))
    c["instructor"] = ask_str("Instructor", c.get("instructor", ""), True)
    c["notes"] = ask_str("Notes", c.get("notes", ""), True)
    return c


def add_course(ctx, admin="admin"):
    c = _course_form(ctx, {}, False)
    courses = fm.load_courses() + [c]
    fm.save_courses(courses)
    names = {x["code"]: x["name_ar"] for x in courses}
    doc = f"course_{c['code']}.txt"
    if doc not in ctx.docs:
        fm.save_document(doc, _course_doc_text(c, names))
    fm.log_event(admin, "ADMIN_ADD_COURSE", c["code"], c["name_en"])
    ctx.reload()
    print("Course added + document created / تمت الإضافة.")


def edit_course(ctx, admin="admin"):
    code = ask_str("Course code to edit").upper()
    if code not in ctx.kb.courses:
        print("Not found.")
        return
    new = _course_form(ctx, dict(ctx.kb.courses[code]), True)
    fm.save_courses([new if c["code"] == code else c for c in fm.load_courses()])
    fm.log_event(admin, "ADMIN_EDIT_COURSE", code, "")
    ctx.reload()
    print("Updated / تم التعديل.")


def delete_course(ctx, admin="admin"):
    code = ask_str("Course code to delete").upper()
    if code not in ctx.kb.courses:
        print("Not found.")
        return
    deps = ctx.kb.dependents(code)
    if deps:
        print("  ! cannot delete: it is a prerequisite of", ", ".join(deps))
        return
    if ask_yes_no(f"Delete {code}?", False):
        fm.save_courses([c for c in fm.load_courses() if c["code"] != code])
        fm.delete_document(f"course_{code}.txt")
        fm.log_event(admin, "ADMIN_DELETE_COURSE", code, "")
        ctx.reload()
        print("Deleted.")


def list_courses(ctx, admin="admin"):
    for c in sorted(ctx.courses, key=lambda c: (c["level"], c["semester"], c["code"])):
        print(f"{c['code']} | {c['name_ar']} | {c['credits']}h | L{c['level']} {c['semester']} | pre: {c['prerequisites'] or '-'}")


def add_document(ctx, admin="admin"):
    name = ask_str("File name (e.g. new_policy)")
    name = re.sub(r"[^\w\-]", "_", name)
    if (name + ".txt") in ctx.docs and not ask_yes_no("Exists. Overwrite?", False):
        return
    text = read_multiline("Type the document (first line = title). Finish with END on its own line:")
    if not text.strip():
        print("Empty document ignored.")
        return
    fm.save_document(name, text)
    fm.log_event(admin, "ADMIN_ADD_DOC", name, f"{len(text)} chars")
    ctx.reload()
    print(f"Saved; index rebuilt ({ctx.doc_engine.stats()}).")


def edit_document(ctx, admin="admin"):
    name = ask_str("Document file name (with .txt)")
    if name not in ctx.docs:
        print("Not found. Available:", ", ".join(list(ctx.docs)[:10]), "...")
        return
    print("--- current text ---\n" + ctx.docs[name])
    mode = ask_str("1) append lines  2) replace all", "1")
    extra = read_multiline("Type text, finish with END:")
    fm.save_document(name, (ctx.docs[name].rstrip("\n") + "\n" + extra) if mode == "1" else extra)
    fm.log_event(admin, "ADMIN_EDIT_DOC", name, "append" if mode == "1" else "replace")
    ctx.reload()
    print("Saved; index rebuilt.")


def delete_document(ctx, admin="admin"):
    name = ask_str("Document file name")
    if name in ctx.docs and ask_yes_no(f"Delete {name}?", False):
        fm.delete_document(name)
        fm.log_event(admin, "ADMIN_DELETE_DOC", name, "")
        ctx.reload()


def add_faq(ctx, admin="admin"):
    faqs = fm.load_faqs()
    faqs.append({"q": ask_str("Question"), "a": ask_str("Answer"), "source": ask_str("Source (e.g. مادة 11)", "", True),
                 "keywords": ask_str("Keywords (optional)", "", True)})
    fm.save_faqs(faqs)
    fm.log_event(admin, "ADMIN_ADD_FAQ", faqs[-1]["q"], "")
    ctx.reload()


def edit_faq(ctx, admin="admin"):
    faqs = fm.load_faqs()
    for i, f in enumerate(faqs, 1):
        print(f"{i}. {f['q']}")
    i = ask_int("FAQ number (0 to cancel)", 0, len(faqs), 0)
    if i:
        f = faqs[i - 1]
        f["q"], f["a"] = ask_str("Question", f["q"]), ask_str("Answer", f["a"])
        f["source"], f["keywords"] = ask_str("Source", f.get("source", ""), True), ask_str("Keywords", f.get("keywords", ""), True)
        fm.save_faqs(faqs)
        fm.log_event(admin, "ADMIN_EDIT_FAQ", f["q"], "")
        ctx.reload()


def delete_faq(ctx, admin="admin"):
    faqs = fm.load_faqs()
    for i, f in enumerate(faqs, 1):
        print(f"{i}. {f['q']}")
    i = ask_int("FAQ number to delete (0 to cancel)", 0, len(faqs), 0)
    if i and ask_yes_no("Sure?", False):
        fm.log_event(admin, "ADMIN_DELETE_FAQ", faqs[i - 1]["q"], "")
        del faqs[i - 1]
        fm.save_faqs(faqs)
        ctx.reload()


def add_staff(ctx, admin="admin"):
    staff = fm.load_staff()
    staff.append({k: ask_str(k, "", k != "name") for k in fm.STAFF_FIELDS})
    fm.save_staff(staff)
    fm.log_event(admin, "ADMIN_ADD_STAFF", staff[-1]["name"], "")
    ctx.reload()


def add_schedule(ctx, admin="admin"):
    row = {}
    while True:
        row["code"] = ask_str("Course code").upper()
        if row["code"] in ctx.kb.courses:
            break
        print("  ! unknown course")
    for k in ("group", "kind", "day", "start", "end", "room", "instructor"):
        row[k] = ask_str(k)
    rows = fm.load_schedule() + [row]
    fm.save_schedule(rows)
    fm.log_event(admin, "ADMIN_ADD_SCHEDULE", row["code"], f"{row['day']} {row['start']}")
    ctx.reload()


def edit_rule(ctx, admin="admin"):
    rules = fm.load_rules()
    simple = {k: v for k, v in rules.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    for k, v in simple.items():
        print(f"  {k} = {v}")
    key = ask_str("Rule key to change (empty to cancel)", "", True)
    if key in simple:
        try:
            val = float(ask_str("New value"))
            rules[key] = int(val) if float(val).is_integer() else val
            fm.save_rules(rules)
            fm.log_event(admin, "ADMIN_EDIT_RULE", key, str(rules[key]))
            ctx.reload()
            print("Rule updated.")
        except ValueError:
            print("Invalid number.")


def stats(ctx, admin="admin"):
    print("Courses:", len(ctx.courses), "| Documents/FAQ index:", ctx.doc_engine.stats(), "| FAQs:", len(ctx.faqs),
          "| Staff:", len(ctx.staff), "| Schedule rows:", len(ctx.schedule))


def admin_menu(ctx):
    if ask_str("Admin password (كلمة المرور)") != config.ADMIN_PASSWORD:
        print("Wrong password.")
        return
    items = [("Add course", add_course), ("Edit course", edit_course), ("Delete course", delete_course),
             ("List courses", list_courses), ("Add document", add_document), ("Edit document", edit_document),
             ("Delete document", delete_document), ("Add FAQ", add_faq), ("Edit FAQ", edit_faq),
             ("Delete FAQ", delete_faq), ("Add staff member", add_staff), ("Add schedule entry", add_schedule),
             ("Change a numeric rule", edit_rule), ("System statistics", stats)]
    while True:
        print("\n=== Admin (المسؤول) ===")
        for i, (name, _) in enumerate(items, 1):
            print(f"{i}. {name}")
        print("0. Back")
        c = ask_int("Choose", 0, len(items), 0)
        if c == 0:
            return
        items[c - 1][1](ctx)
