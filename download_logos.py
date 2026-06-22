import urllib.request
import os

logos = {
    'logo-amil.png': 'https://logo.clearbit.com/amil.com.br',
    'logo-hapvida.png': 'https://logo.clearbit.com/hapvida.com.br',
    'logo-porto.png': 'https://logo.clearbit.com/portoseguro.com.br',
    'logo-sulamerica.png': 'https://logo.clearbit.com/sulamerica.com.br',
    'logo-unimed.png': 'https://logo.clearbit.com/unimed.coop.br',
    'logo-bradesco.png': 'https://logo.clearbit.com/bradescoseguros.com.br',
    'logo-fbn.png': 'https://brokers.grupofbn.com.br/wp-content/uploads/2021/04/FBN-Brokers-300x127.png'
}

for filename, url in logos.items():
    try:
        # User-agent is often required to not get blocked
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
