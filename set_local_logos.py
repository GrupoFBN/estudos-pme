import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace clearbit URLs with local filenames
mapping = {
    'https://logo.clearbit.com/amil.com.br': 'logo-amil.png',
    'https://logo.clearbit.com/hapvida.com.br': 'logo-hapvida.png',
    'https://logo.clearbit.com/portoseguro.com.br': 'logo-porto.png',
    'https://logo.clearbit.com/sulamerica.com.br': 'logo-sulamerica.png',
    'https://logo.clearbit.com/unimed.coop.br': 'logo-unimed.png',
    'https://logo.clearbit.com/bradescoseguros.com.br': 'logo-bradesco.png'
}

for url, local in mapping.items():
    content = content.replace(url, local)

# Fix FBN logo
content = content.replace('https://brokers.grupofbn.com.br/wp-content/uploads/2021/04/FBN-Brokers-300x127.png', 'logo-fbn.png')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
