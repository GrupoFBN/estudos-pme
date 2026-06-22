import os

logo_dir = 'assets/logos'
try:
    for filename in os.listdir(logo_dir):
        if ' ' in filename:
            new_name = filename.replace(' ', '-')
            os.rename(os.path.join(logo_dir, filename), os.path.join(logo_dir, new_name))
except Exception as e:
    print(e)

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

mapping = {
    'assets/logos/logo amil.png': 'assets/logos/logo-amil.png',
    'assets/logos/logo hapvida.png': 'assets/logos/logo-hapvida.png',
    'assets/logos/logo porto saude.png': 'assets/logos/logo-porto-saude.png',
    'assets/logos/logo sulamerica.png': 'assets/logos/logo-sulamerica.png',
    'assets/logos/logo unimed.png': 'assets/logos/logo-unimed.png',
    'assets/logos/logo fbn.png': 'assets/logos/logo-fbn.png'
}

for old, new in mapping.items():
    content = content.replace(old, new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
