import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add a cache buster parameter to all png images inside assets/logos
# so the browser is forced to reload them instead of using the broken cache
content = re.sub(r'(\./assets/logos/[^"]+\.png)', r'\1?v=2', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
