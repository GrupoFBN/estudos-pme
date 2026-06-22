"""
Debug RLA with word-level coordinates to understand column layout.
"""
import pdfplumber
import re

with pdfplumber.open('FRI/RLA_22_06_2026.pdf') as pdf:
    page = pdf.pages[1]  # page 2
    words = page.extract_words()
    
    print("Words with X positions (first 60):")
    for w in words[:60]:
        print(f"  x0={w['x0']:6.1f} x1={w['x1']:6.1f} y={w['top']:6.1f}  text={repr(w['text'])}")
    
    print("\n\nPage 1 words (first 50):")
    page1 = pdf.pages[0]
    words1 = page1.extract_words()
    for w in words1[:50]:
        print(f"  x0={w['x0']:6.1f} x1={w['x1']:6.1f} y={w['top']:6.1f}  text={repr(w['text'])}")
