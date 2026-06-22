import base64

filepath = 'assets/logos/bradesco-logo.png'
with open(filepath, 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
data_uri = f'data:image/png;base64,{encoded}'

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the SVG placeholder with the real Bradesco logo
# Find the current bradesco logo value (it's the SVG base64 we put before)
import re
content = re.sub(r'logo: "data:image/svg\+xml;base64,[^"]+",', f'logo: "{data_uri}",', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
