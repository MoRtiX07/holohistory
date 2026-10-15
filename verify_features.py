import urllib.request
import json
import time

base_url = 'http://127.0.0.1:8000'

print("=== 1. Testing /api/personas Endpoint ===")
req = urllib.request.urlopen(f"{base_url}/api/personas")
personas = json.loads(req.read().decode())
print(f"Retrieved {len(personas)} personas.")
for p in personas:
    artifacts = p.get("artifacts", [])
    surprises = p.get("surprises", [])
    print(f" - {p['name']}: {len(artifacts)} artifacts, {len(surprises)} surprise questions")
    for a in artifacts:
        # Check image availability
        img_url = f"{base_url}{a['image']}"
        img_code = urllib.request.urlopen(img_url).getcode()
        print(f"    * Artifact: '{a['title']}' ({a['year']}) -> Image status {img_code}")

print("\n=== 2. Testing Chat Endpoint with Einstein Artifact Prompt ===")
test_artifact_payload = {
    "persona": "einstein",
    "message": "Explain your work on Spacetime Curvature and E=mc2.",
    "history": []
}
t0 = time.time()
req = urllib.request.Request(
    f"{base_url}/api/chat",
    data=json.dumps(test_artifact_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
t_diff = time.time() - t0
print(f"Latency: {t_diff:.2f}s")
print(f"Grounded Chunks: {len(res.get('chunks', []))}")
print(f"Response: {res.get('response')}\n")

print("=== 3. Testing Chat Endpoint with Tesla Surprise Question ===")
surprise_q = personas[2]["surprises"][0]
print(f"Surprise Question: '{surprise_q}'")
test_surprise_payload = {
    "persona": "tesla",
    "message": surprise_q,
    "history": []
}
t0 = time.time()
req = urllib.request.Request(
    f"{base_url}/api/chat",
    data=json.dumps(test_surprise_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
t_diff = time.time() - t0
print(f"Latency: {t_diff:.2f}s")
print(f"Grounded Chunks: {len(res.get('chunks', []))}")
print(f"Response: {res.get('response')}\n")

print("=== 4. Testing Chat Endpoint with Kalam Aerospace Work ===")
kalam_q = personas[1]["artifacts"][0]["prompt"]
print(f"Kalam Work Prompt: '{kalam_q}'")
test_kalam_payload = {
    "persona": "kalam",
    "message": kalam_q,
    "history": []
}
t0 = time.time()
req = urllib.request.Request(
    f"{base_url}/api/chat",
    data=json.dumps(test_kalam_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
t_diff = time.time() - t0
print(f"Latency: {t_diff:.2f}s")
print(f"Grounded Chunks: {len(res.get('chunks', []))}")
print(f"Response: {res.get('response')}\n")

print("SUCCESS: All tests passed!")
