"""Knowledge Representation: facts (courses.csv) + rules (rules.json) + inference.

Facts   : prerequisite(C, P), credits(C, n), level(C, n), semester(C, s), completed(Student, C)
Rules   : R1 not already passed          R2 all prerequisites passed
          R3 minimum passed credits      R4 course offered in chosen semester
          R5 credit-load limit by CGPA   R6 level from passed credits
          R7 academic warning / dismissal R8 graduation & honors checks
Every rule returns an explanation (reason) in Arabic, not just yes/no."""
from collections import Counter

SEM_AR = {"First": "الأول", "Second": "الثاني"}


class KnowledgeBase:
    def __init__(self, courses, rules):
        self.rules = rules
        self.courses = {c["code"]: c for c in courses}
        self.prereq = {code: [p.strip() for p in (c.get("prerequisites") or "").split(";") if p.strip()]
                       for code, c in self.courses.items()}

    # ---------- facts ----------
    def credits(self, code):
        return int(self.courses[code].get("credits") or 0)

    def label(self, code):
        c = self.courses.get(code)
        return f"{code} ({c['name_ar']})" if c else code

    def passed_credits(self, student):
        return sum(self.credits(c) for c in set(student.get("completed", [])) if c in self.courses)

    def remaining_credits(self, student):
        return max(0, self.rules["graduation_credits"] - self.passed_credits(student))

    def dependents(self, code):
        """Courses that require `code` directly."""
        return [c for c, p in self.prereq.items() if code in p]

    def full_prereq_chain(self, code):
        """All direct + indirect prerequisites (forward chaining over the prerequisite facts)."""
        chain, stack = set(), list(self.prereq.get(code, []))
        while stack:
            p = stack.pop()
            if p not in chain:
                chain.add(p)
                stack.extend(self.prereq.get(p, []))
        return sorted(chain)

    # ---------- R6 level ----------
    def level_of(self, student):
        passed = self.passed_credits(student)
        for t in self.rules["level_thresholds"]:
            if passed >= t["min_passed"]:
                return t["level"]
        return 1

    # ---------- R5 credit load ----------
    def max_credits(self, student, summer=False, graduating=False):
        r = self.rules
        if summer:
            return r["max_credits_summer"]
        if graduating:
            return r["max_credits_graduating"]
        if student.get("first_semester"):
            return r["max_credits_first_semester"]
        cgpa = float(student.get("cgpa", 0))
        for tier in sorted(r["max_credits_by_cgpa"], key=lambda t: -t["min_cgpa"]):
            if cgpa >= tier["min_cgpa"]:
                return tier["max"]
        return 12

    # ---------- R1-R4 eligibility ----------
    def check(self, student, code, semester=None):
        """Return (eligible, [reasons])."""
        if code not in self.courses:
            return False, ["المقرر غير موجود في الخطة الدراسية"]
        c = self.courses[code]
        done = set(student.get("completed", []))
        if code in done:
            return False, ["تم اجتيازه من قبل (يمكن إعادته للتحسين فقط - مادة 20)"]
        reasons = []
        if code == "MA111" and not student.get("science_stream"):
            reasons.append("رياضيات 0 لطلبة علمي علوم فقط (مادة 4)")
        missing = [p for p in self.prereq[code] if p not in done]
        if missing:
            reasons.append("متطلبات سابقة لم تُجتز: " + "، ".join(self.label(p) for p in missing))
        need = int(c.get("min_passed_credits") or 0)
        if need and self.passed_credits(student) < need:
            reasons.append(f"يتطلب اجتياز {need} ساعة معتمدة على الأقل (اجتزت {self.passed_credits(student)})")
        if semester in SEM_AR and c["semester"] != semester:
            reasons.append(f"يُطرح في الفصل {SEM_AR[c['semester']]} وليس الفصل {SEM_AR[semester]}")
        return not reasons, reasons

    def eligible_courses(self, student, semester=None):
        out = [c for c in self.courses if self.check(student, c, semester)[0]]
        return sorted(out, key=lambda c: (int(self.courses[c]["level"]), c))

    def explain_all(self, student, semester=None):
        return {c: self.check(student, c, semester) for c in self.courses}

    # ---------- plan validation (R1-R5) ----------
    def validate_plan(self, student, codes, semester=None):
        codes = list(dict.fromkeys(codes))
        problems, total = [], 0
        for code in codes:
            ok, reasons = self.check(student, code, semester)
            if code in self.courses:
                total += self.credits(code)
            if not ok:
                problems.append(f"{self.label(code)}: " + " - ".join(reasons))
        remaining = self.remaining_credits(student)
        graduating = remaining > 0 and total >= remaining
        mx = self.max_credits(student, summer=(semester == "Summer"), graduating=graduating)
        mn = self.rules["min_credits_regular"]
        if total > mx:
            problems.append(f"مجموع الساعات {total} أكبر من الحد الأقصى المسموح {mx}")
        if semester != "Summer" and total < mn and remaining >= mn:
            problems.append(f"مجموع الساعات {total} أقل من الحد الأدنى {mn}")
        return {"ok": not problems, "total": total, "min": mn, "max": mx, "problems": problems}

    def suggest_plan(self, student, semester):
        """Greedy plan: core courses first (lower levels first), then allowed electives, within the credit cap."""
        mx = self.max_credits(student, summer=(semester == "Summer"))
        lvl = self.level_of(student)   # suggest only courses up to the student's current level
        elig = [c for c in self.eligible_courses(student, None if semester == "Summer" else semester)
                if int(self.courses[c]["level"]) <= lvl]
        core = [c for c in elig if self.courses[c]["status"] == "Core"]
        elect = [c for c in elig if self.courses[c]["status"] == "Elective"]
        picks = Counter()
        for c in student.get("completed", []):
            if c in self.courses and self.courses[c]["status"] == "Elective":
                picks[self._group(c)] += 1
        plan, total = [], 0
        for code in core + elect:
            cr = self.credits(code)
            if self.courses[code]["status"] == "Elective":
                g = self._group(code)
                if picks[g] >= self.rules["elective_picks"].get(g, 0):
                    continue
                if total + cr > mx:
                    continue
                picks[g] += 1
            elif total + cr > mx:
                continue
            plan.append(code)
            total += cr
        return plan, total, mx

    def _group(self, code):
        c = self.courses[code]
        return f"{c['level']}-{c['semester']}"

    # ---------- R7 academic status ----------
    def general_grade(self, cgpa):
        for g in sorted(self.rules["general_grade"], key=lambda g: -g["min"]):
            if cgpa >= g["min"]:
                return g["name"]
        return ""

    def academic_status(self, student):
        r = self.rules
        cgpa = float(student.get("cgpa", 0))
        first = bool(student.get("first_semester"))
        passed, remaining = self.passed_credits(student), self.remaining_credits(student)
        warning = cgpa < r["warning_cgpa_below"] and not first
        cons = int(student.get("consecutive_warnings", 0)) + (1 if warning else 0)
        total = int(student.get("total_warnings", 0)) + (1 if warning else 0)
        d = r["dismissal"]
        at_risk = cons >= d["consecutive_warnings"] or total >= d["total_warnings"]
        msgs = []
        if first:
            msgs.append("أنت في فصلك الأول: لا يوجد إنذار أكاديمي في الفصل الأول (مادة 22).")
        if warning:
            msgs.append(f"معدلك {cgpa} أقل من {r['warning_cgpa_below']}: إنذار أكاديمي ووضع تحت الملاحظة الأكاديمية (مادة 22). "
                        f"يمكنك إعادة مقررات نجحت فيها لرفع المعدل (مادة 20).")
        if at_risk:
            msgs.append(f"تحذير: إنذارات متتالية {cons} / متفرقة {total} - الفصل عند {d['consecutive_warnings']} متتالية أو {d['total_warnings']} متفرقة.")
        elif warning and (cons == d["consecutive_warnings"] - 1 or total == d["total_warnings"] - 1):
            msgs.append("تنبيه: تبقى إنذار واحد قبل الوصول لحد الفصل.")
        if not msgs:
            msgs.append("وضعك الأكاديمي سليم.")
        return {"level": self.level_of(student), "passed": passed, "remaining": remaining, "cgpa": cgpa,
                "general_grade": self.general_grade(cgpa), "warning": warning, "dismissal_risk": at_risk,
                "max_credits": self.max_credits(student), "messages": msgs}

    # ---------- R8 graduation / honors ----------
    def graduation_check(self, student):
        r, done = self.rules, set(student.get("completed", []))
        missing = []
        rem = self.remaining_credits(student)
        if rem:
            missing.append(f"باقي {rem} ساعة معتمدة من {r['graduation_credits']}")
        if float(student.get("cgpa", 0)) < r["min_cgpa_graduation"]:
            missing.append(f"المعدل التراكمي أقل من {r['min_cgpa_graduation']}")
        if not student.get("training_done"):
            missing.append("التدريب الميداني الصيفي")
        for g in ("GP411", "GP421"):
            if g not in done:
                missing.append(f"مشروع التخرج: {self.label(g)}")
        if student.get("science_stream") and "MA111" not in done:
            missing.append("رياضيات 0 (شرط لطلبة علمي علوم)")
        return not missing, missing

    def honors_check(self, student):
        r, reasons = self.rules, []
        if float(student.get("cgpa", 0)) < r["honors_min_cgpa"]:
            reasons.append(f"المعدل التراكمي أقل من {r['honors_min_cgpa']}")
        if int(student.get("semesters_studied", 0)) > r["honors_max_semesters"]:
            reasons.append("مدة الدراسة تزيد عن 8 فصول نظامية")
        if student.get("ever_failed"):
            reasons.append("سبق الرسوب أو الحرمان في مقرر")
        return not reasons, reasons

    # ---------- grading helpers (articles 13, 15) ----------
    def grade_for_percent(self, percent):
        for g in sorted(self.rules["grade_scale"], key=lambda g: -g["min"]):
            if percent >= g["min"]:
                return g["letter"], g["points"]
        return "F", 0.0

    def course_result(self, total_percent, final_exam_percent):
        """Apply the 30%-of-final-exam rule (article 13)."""
        if final_exam_percent < self.rules["min_final_exam_percent"]:
            return "راسب لائحة", "F", 0.0
        letter, pts = self.grade_for_percent(total_percent)
        return ("ناجح" if total_percent >= self.rules["pass_percent"] else "راسب"), letter, pts

    @staticmethod
    def calc_gpa(entries):
        """entries = [(credits, points)] -> GPA"""
        hours = sum(c for c, _ in entries)
        return round(sum(c * p for c, p in entries) / hours, 2) if hours else 0.0

    def attendance_status(self, absence_percent):
        a = self.rules["attendance"]
        if absence_percent > a["deprivation_absence"]:
            return "deprived", "نسبة الغياب تجاوزت 25%: معرض للحرمان من الامتحان النهائي بعد الإنذار (درجة صفر في النهائي)."
        if absence_percent >= a["warning_absence"]:
            return "warning", "نسبة الغياب وصلت 20% أو أكثر: يوجه لك إنذار غياب."
        return "ok", "نسبة الغياب في الحدود الآمنة."
