"""Central place for all file paths and settings."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "docs")
COURSES_CSV = os.path.join(DATA_DIR, "courses.csv")
STAFF_CSV = os.path.join(DATA_DIR, "staff.csv")
SCHEDULE_CSV = os.path.join(DATA_DIR, "schedule.csv")
FAQS_JSON = os.path.join(DATA_DIR, "faqs.json")
RULES_JSON = os.path.join(DATA_DIR, "rules.json")
STUDENTS_JSON = os.path.join(DATA_DIR, "students.json")
LOG_FILE = os.path.join(BASE_DIR, "logs", "query_log.txt")

ADMIN_PASSWORD = "admin123"   # simple demo password for the admin interface
FAQ_THRESHOLD = 0.5           # FAQ answer is shown directly if cosine >= this
TOP_K_DOCS = 3
