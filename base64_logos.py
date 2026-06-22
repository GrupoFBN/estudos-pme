import base64
import re
import os

def get_base64(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Map the logo variables in JS to base64
logo_amil = get_base64('assets/logos/logo-amil.png')
logo_hapvida = get_base64('assets/logos/logo-hapvida.png')
logo_porto = get_base64('assets/logos/logo-porto-saude.png')
logo_sulamerica = get_base64('assets/logos/logo-sulamerica.png')
logo_unimed = get_base64('assets/logos/logo-unimed.png')
logo_fbn = get_base64('assets/logos/Logo-FBN-azul.png')

# Also handle logo-bradesco if they eventually add it, or just fallback
# But right now we replace the specific ones

if logo_amil:
    content = re.sub(r'logo:\s*".*logo-amil.png.*?",', f'logo: "{logo_amil}",', content)
if logo_hapvida:
    content = re.sub(r'logo:\s*".*logo-hapvida.png.*?",', f'logo: "{logo_hapvida}",', content)
if logo_porto:
    content = re.sub(r'logo:\s*".*logo-porto-saude.png.*?",', f'logo: "{logo_porto}",', content)
if logo_sulamerica:
    content = re.sub(r'logo:\s*".*logo-sulamerica.png.*?",', f'logo: "{logo_sulamerica}",', content)
if logo_unimed:
    content = re.sub(r'logo:\s*".*logo-unimed.png.*?",', f'logo: "{logo_unimed}",', content)

# Fix FBN in the HTML header
if logo_fbn:
    content = re.sub(r'src="\./assets/logos/Logo-FBN-azul\.png.*?"', f'src="{logo_fbn}"', content)
    content = re.sub(r'src="assets/logos/Logo-FBN-azul\.png.*?"', f'src="{logo_fbn}"', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done encoding to base64!')
