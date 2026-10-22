import math, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from context import Context
from search_engine import SearchEngine, tokenize
import file_manager as fm


class TestSearch(unittest.TestCase):
    def test_arabic_normalisation(self):
        self.assertEqual(tokenize("الغياب"), tokenize("بالغياب"))
        self.assertEqual(tokenize("الإنذار"), tokenize("انذار"))

    def test_tfidf_cosine_by_hand(self):
        e = SearchEngine()
        e.build({"d1": "python programming language", "d2": "python snake", "d3": "java programming language"})
        res = dict(e.search("python programming", 3))
        # manual: idf(python)=ln(3/2)+1, idf(programming)=ln(3/2)+1
        idf = math.log(1.5) + 1
        q = [idf, idf]; d1 = [idf, idf, math.log(3 / 2) + 1]
        d1 = [idf, idf, idf]  # python, programming, language
        expected = (idf * idf * 2) / (math.sqrt(2) * idf * math.sqrt(3) * idf)
        self.assertAlmostEqual(res["d1"], expected, places=6)
        self.assertEqual(max(res, key=res.get), "d1")

    def test_ranking_on_regulation(self):
        c = Context()
        top = c.doc_engine.search("نسبة الحضور والغياب", 1)[0][0]
        self.assertEqual(top, "regulation_attendance.txt")
        top = c.doc_engine.search("مشروع التخرج", 3)
        self.assertIn("regulation_project.txt", [d for d, _ in top])

    def test_faq(self):
        c = Context()
        a = c.answer_question("نسبة الحضور المطلوبة ايه؟")
        self.assertEqual(a["type"], "faq")
        self.assertIn("75%", a["answer"])

    def test_empty_query(self):
        self.assertEqual(Context().doc_engine.search("؟؟ !!", 3), [])


class TestKB(unittest.TestCase):
    def setUp(self):
        self.kb = Context().kb
        self.s1 = fm.get_student("S001")

    def test_eligible(self):
        e = self.kb.eligible_courses(self.s1, "First")
        for c in ("ML211", "BC211", "ES211", "MA212"):
            self.assertIn(c, e)
        self.assertNotIn("BC312", e)

    def test_reason(self):
        ok, r = self.kb.check(self.s1, "BC312")
        self.assertFalse(ok); self.assertIn("BC223", r[0])

    def test_chain(self):
        self.assertIn("MA112", self.kb.full_prereq_chain("ML311"))

    def test_levels_and_limits(self):
        self.assertEqual(self.kb.level_of({"completed": []}), 1)
        self.assertEqual(self.kb.level_of(self.s1), 2)
        self.assertEqual(self.kb.max_credits({"cgpa": 3.2}), 21)
        self.assertEqual(self.kb.max_credits({"cgpa": 2.0}), 18)
        self.assertEqual(self.kb.max_credits({"cgpa": 1.5}), 15)
        self.assertEqual(self.kb.max_credits({"cgpa": 0.5}), 12)
        self.assertEqual(self.kb.max_credits({"cgpa": 3.9, "first_semester": True}), 18)
        self.assertEqual(self.kb.max_credits({"cgpa": 3.9}, summer=True), 9)

    def test_plan(self):
        low = dict(self.s1, cgpa=1.5)
        r = self.kb.validate_plan(low, ["ML211", "BC211", "BC212", "ES211", "RB211", "HU211"], "First")
        self.assertFalse(r["ok"])  # 16 > 15
        r = self.kb.validate_plan(self.s1, ["ML211", "BC211", "BC212"], "First")
        self.assertTrue(r["ok"])

    def test_project_rule(self):
        ok, r = self.kb.check(self.s1, "GP411")
        self.assertFalse(ok)

    def test_grades(self):
        self.assertEqual(self.kb.grade_for_percent(96), ("A+", 4.0))
        self.assertEqual(self.kb.grade_for_percent(50), ("D-", 1.0))
        self.assertEqual(self.kb.course_result(70, 20)[0], "راسب لائحة")
        self.assertEqual(self.kb.calc_gpa([(3, 4.0), (3, 2.0)]), 3.0)

    def test_status(self):
        self.assertTrue(fm.get_student("S003") and self.kb.academic_status(fm.get_student("S003"))["warning"])
        self.assertFalse(self.kb.academic_status(fm.get_student("S002"))["warning"])
        self.assertEqual(self.kb.attendance_status(26)[0], "deprived")
        self.assertEqual(self.kb.attendance_status(20)[0], "warning")
        self.assertEqual(self.kb.attendance_status(5)[0], "ok")

    def test_data_integrity(self):
        for c, pres in self.kb.prereq.items():
            for p in pres:
                self.assertIn(p, self.kb.courses, f"{c} -> {p}")
        self.assertEqual(len(self.kb.courses), 63)


if __name__ == "__main__":
    unittest.main(verbosity=2)
