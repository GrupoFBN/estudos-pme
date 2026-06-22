import pdfplumber, re

with pdfplumber.open('FRI/RLA_22_06_2026.pdf') as pdf:
    full_text = ''
    for page in pdf.pages:
        full_text += (page.extract_text() or '') + '\n'

lines = [l.strip() for l in full_text.split('\n') if l.strip()]

# Find the list start and print lines after
for i, ln in enumerate(lines):
    if 'Relat' in ln and 'vidas' in ln.lower():
        print(f'Found list at line {i}')
        for j in range(i, min(i+60, len(lines))):
            print(f'{j:3}: {repr(lines[j])}')
        break

print("\n\n=== Testing regex patterns ===")
# Test the person_line_re
person_line_re = re.compile(
    r'(\d{10,})\s+(\d{11})\s+(Titular|Dependente)\s+(\d{2}/\d{2}/\d{4})'
    r'.*?BRL([\d\.,]+)\s*BRL([\d\.,]+)\s*BRL([\d\.,]+)\s*BRL([\d\.,]+)\s*BRL([\d\.,]+)'
)

for i, ln in enumerate(lines):
    m = person_line_re.search(ln)
    if m:
        print(f'MATCH line {i}: {repr(ln[:80])}')
        print(f'  cart={m.group(1)}, titularidade={m.group(3)}, valor={m.group(9)}')
    elif re.search(r'\d{10,}', ln):
        print(f'HAS DIGITS line {i}: {repr(ln[:100])}')
