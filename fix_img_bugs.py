import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix FBN logo to the actual name the user used
content = content.replace('assets/logos/logo-fbn.png', 'assets/logos/Logo-FBN-azul.png')

# Remove referrerpolicy="no-referrer" which can block local images in some browsers
content = content.replace(' referrerpolicy="no-referrer"', '')

# Prepend ./ to assets/logos to ensure relative path resolution works everywhere
content = content.replace('"assets/logos/', '"./assets/logos/')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
