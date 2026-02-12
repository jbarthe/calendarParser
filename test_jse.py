from parser import parse_extra_days
import pandas as pd

def test_parse():
    cases = [
        "(+2 JS : 24 et 25/02/26)",
        "(+1 JS : 28/02/26)",
        "(+2 JS :30/04 et 02/05/26)",
        "Du 01/01/25 au 05/01/25 (+1 JS : 10/01/25)",
        "No JS here"
    ]
    
    for c in cases:
        print(f"Input: {c}")
        res = parse_extra_days(c)
        print(f"Output: {res}")
        print("-" * 20)

if __name__ == "__main__":
    test_parse()
