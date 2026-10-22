"""All file I/O: CSV, JSON, TXT and the query log."""
import csv
import json
import os
from datetime import datetime

import config

COURSE_FIELDS = ["code", "name_ar", "name_en", "credits", "level", "semester", "status",
                 "type", "prerequisites", "min_passed_credits", "instructor", "notes"]
STAFF_FIELDS = ["name", "title", "department", "office", "email", "office_hours"]
SCHEDULE_FIELDS = ["code", "group", "kind", "day", "start", "end", "room", "instructor"]


def _warn(msg):
    print(f"[warning] {msg}")


# ---------------- CSV ----------------
def _read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:   # utf-8-sig keeps Excel files safe
            return list(csv.DictReader(f))
    except FileNotFoundError:
        _warn(f"file not found: {path}")
    except (OSError, csv.Error) as e:
        _warn(f"cannot read {path}: {e}")
    return []


def _write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_courses():
    return _read_csv(config.COURSES_CSV)


def save_courses(courses):
    _write_csv(config.COURSES_CSV, COURSE_FIELDS, courses)


def load_staff():
    return _read_csv(config.STAFF_CSV)


def save_staff(staff):
    _write_csv(config.STAFF_CSV, STAFF_FIELDS, staff)


def load_schedule():
    return _read_csv(config.SCHEDULE_CSV)


def save_schedule(rows):
    _write_csv(config.SCHEDULE_CSV, SCHEDULE_FIELDS, rows)


# ---------------- JSON ----------------
def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        _warn(f"file not found: {path}")
    except (OSError, json.JSONDecodeError) as e:
        _warn(f"cannot read {path}: {e}")
    return default


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_rules():
    return load_json(config.RULES_JSON, {})


def save_rules(rules):
    save_json(rules, config.RULES_JSON)


def load_faqs():
    return load_json(config.FAQS_JSON, [])


def save_faqs(faqs):
    save_json(faqs, config.FAQS_JSON)


def load_students():
    return load_json(config.STUDENTS_JSON, [])


def save_student(student):
    """Insert or update one student record (matched by id)."""
    students = load_students()
    for i, s in enumerate(students):
        if s["id"] == student["id"]:
            students[i] = student
            break
    else:
        students.append(student)
    save_json(students, config.STUDENTS_JSON)


def get_student(student_id):
    for s in load_students():
        if s["id"] == student_id:
            return s
    return None


# ---------------- TXT documents ----------------
def load_documents():
    docs = {}
    try:
        for name in sorted(os.listdir(config.DOCS_DIR)):
            if name.endswith(".txt"):
                with open(os.path.join(config.DOCS_DIR, name), encoding="utf-8") as f:
                    docs[name] = f.read()
    except OSError as e:
        _warn(f"cannot read docs folder: {e}")
    return docs


def save_document(name, text):
    if not name.endswith(".txt"):
        name += ".txt"
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    with open(os.path.join(config.DOCS_DIR, name), "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    return name


def delete_document(name):
    try:
        os.remove(os.path.join(config.DOCS_DIR, name))
        return True
    except OSError:
        return False


# ---------------- Log ----------------
def log_event(user, action, query, summary=""):
    """Append one line: time | user | ACTION | query | summary"""
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    clean = lambda s: str(s).replace("\n", " ").replace("|", "/")
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {clean(user)} | {action} | {clean(query)} | {clean(summary)}\n")
