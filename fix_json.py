import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken label: "314.15
pattern = r'\{\s*label:\s*"314\.15,\s*348\.41,\s*354\.58,\s*394\.19,\s*555\.42,\s*621\.82,\s*1412\.71\]\s*\}\s*,'
replacement = r'{ label: "29 a 33",   values: [314.15, 348.41, 354.58, 394.19, 555.42, 621.82, 1412.71] },'
content = re.sub(pattern, replacement, content)

# Remove multiple blank lines
content = re.sub(r'\n{3,}', '\n\n', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
