"""
Debug: inspect RLA to find plan names for each person using coordinate-based approach.
Show all persons and which plan words were found nearby.
"""
import pdfplumber
import re

COL_NAME_MAX   = 73
COL_PLAN_MIN   = 210
COL_PLAN_MAX   = 285

with pdfplumber.open('FRI/RLA_22_06_2026.pdf') as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    
    # Sort by y then x
    sorted_words = sorted(words, key=lambda w: (round(w['top'], 0), w['x0']))
    
    # Group into rows
    rows_dict = {}
    for w in sorted_words:
        y_key = round(w['top'] / 2) * 2
        if y_key not in rows_dict:
            rows_dict[y_key] = []
        rows_dict[y_key].append(w)
    
    rows = [(y, ws) for y, ws in sorted(rows_dict.items())]
    
    # Print first 30 rows showing column assignments
    print("=== PAGE 1: Column assignments ===")
    for y, rwords in rows[:50]:
        name_col = [w['text'] for w in rwords if w['x0'] < COL_NAME_MAX]
        cart_col = [w['text'] for w in rwords if 73 <= w['x0'] < 155]
        cpf_col = [w['text'] for w in rwords if 155 <= w['x0'] < 210]
        plan_col = [w['text'] for w in rwords if COL_PLAN_MIN <= w['x0'] < COL_PLAN_MAX]
        data_col = [w['text'] for w in rwords if w['x0'] >= 285]
        
        if any([name_col, cart_col, cpf_col, plan_col, data_col]):
            print(f"y={y:5.1f} | name={name_col} | cart={cart_col} | cpf={cpf_col} | plan={plan_col} | data={data_col[:3]}")
