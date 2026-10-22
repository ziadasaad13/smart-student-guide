"""Small helpers for validated console input."""
import re


def ask_str(prompt, default=None, allow_empty=False):
    while True:
        hint = f" [{default}]" if default not in (None, "") else ""
        val = input(f"{prompt}{hint}: ").strip()
        if not val and default is not None:
            return default
        if val or allow_empty:
            return val
        print("  ! value required / القيمة مطلوبة")


def ask_int(prompt, lo=None, hi=None, default=None):
    while True:
        raw = ask_str(prompt, None if default is None else str(default))
        try:
            v = int(raw)
        except ValueError:
            print("  ! enter an integer / أدخل رقما صحيحا")
            continue
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            print(f"  ! must be between {lo} and {hi}")
            continue
        return v


def ask_float(prompt, lo=None, hi=None, default=None):
    while True:
        raw = ask_str(prompt, None if default is None else str(default))
        try:
            v = float(raw)
        except ValueError:
            print("  ! enter a number / أدخل رقما")
            continue
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            print(f"  ! must be between {lo} and {hi}")
            continue
        return v


def ask_yes_no(prompt, default=False):
    d = "y" if default else "n"
    while True:
        v = ask_str(f"{prompt} (y/n)", d).lower()
        if v in ("y", "yes", "ن", "نعم"):
            return True
        if v in ("n", "no", "ل", "لا"):
            return False


def read_multiline(prompt="Enter text, finish with a line containing only END"):
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def parse_codes(text):
    """'bc211, ml211;MA112' -> ['BC211','ML211','MA112']"""
    return [c.upper() for c in re.split(r"[,\s;،]+", text.strip()) if c]
