import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

mapping = {
    'logo-amil.png': 'assets/logos/logo amil.png',
    'logo-hapvida.png': 'assets/logos/logo hapvida.png',
    'logo-porto.png': 'assets/logos/logo porto saude.png',
    'logo-sulamerica.png': 'assets/logos/logo sulamerica.png',
    'logo-unimed.png': 'assets/logos/logo unimed.png',
    'logo-fbn.png': 'assets/logos/logo fbn.png'
}

for old, new in mapping.items():
    content = content.replace(old, new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
