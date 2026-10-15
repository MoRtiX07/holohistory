import urllib.request
import os

os.makedirs('static/images', exist_ok=True)
headers = {'User-Agent': 'HologramPersonaChatbot/1.0 (educational research demo; mailto:student@edu.org)'}

urls = {
    'einstein.jpg': 'https://upload.wikimedia.org/wikipedia/commons/d/d3/Albert_Einstein_Head.jpg',
    'kalam.jpg': 'https://upload.wikimedia.org/wikipedia/commons/b/b0/A._P._J._Abdul_Kalam_2015.jpg',
    'tesla.jpg': 'https://upload.wikimedia.org/wikipedia/commons/7/79/Tesla_circa_1890.jpeg'
}

for name, url in urls.items():
    dest = os.path.join('static', 'images', name)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        with open(dest, 'wb') as f:
            f.write(data)
        print(f"Downloaded {name} successfully: {len(data)} bytes")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
