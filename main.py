"""Smart Student Guide - Faculty of AI, Kafrelsheikh University."""
import sys

from admin import admin_menu
from context import Context
from student import student_menu

BANNER = """
==============================================
 Smart Student Guide - دليل الطالب الذكي
 كلية الذكاء الاصطناعي - جامعة كفر الشيخ
=============================================="""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ctx = Context()
    print(BANNER)
    try:
        while True:
            print("\n1. Student (طالب)\n2. Admin (مسؤول)\n3. Exit (خروج)")
            c = input("Choose: ").strip()
            if c == "1":
                student_menu(ctx)
            elif c == "2":
                admin_menu(ctx)
            elif c == "3":
                break
            else:
                print("Invalid choice.")
    except (EOFError, KeyboardInterrupt):
        print()
    print("Bye / مع السلامة")


if __name__ == "__main__":
    main()
