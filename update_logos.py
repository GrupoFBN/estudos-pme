import codecs
import re

with open('index.html', 'rb') as f:
    raw = f.read()
    
# Detect encoding
if raw.startswith(codecs.BOM_UTF16_LE):
    content = raw.decode('utf-16-le')
elif raw.startswith(codecs.BOM_UTF16_BE):
    content = raw.decode('utf-16-be')
else:
    content = raw.decode('utf-8', errors='ignore')

# Add logo mapping
mapping = {
    'amil': 'https://logo.clearbit.com/amil.com.br',
    'hapvida': 'https://logo.clearbit.com/hapvida.com.br',
    'porto': 'https://logo.clearbit.com/portoseguro.com.br',
    'sulam': 'https://logo.clearbit.com/sulamerica.com.br',
    'unimed': 'https://logo.clearbit.com/unimed.coop.br',
    'bradesco': 'https://logo.clearbit.com/bradescoseguros.com.br'
}

# First, remove existing logo lines
content = re.sub(r'\s*logo:\s*\"[^\"]+\",', '', content)

# Replace the FBN logo header image
content = content.replace('src="logo.png"', 'src="https://brokers.grupofbn.com.br/wp-content/uploads/2021/04/FBN-Brokers-300x127.png"')

def replacer(match):
    full_text = match.group(0)
    company_name = match.group(2).lower()
    logo_url = None
    for key, url in mapping.items():
        if key in company_name:
            logo_url = url
            break
    
    if logo_url:
        return full_text + f'\n    logo: "{logo_url}",'
    return full_text

# match company line
pattern = r'(company:\s*[\'\"]([^\'\"]+)[\'\"]\s*,)'
content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)

# Write back as utf-8
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
