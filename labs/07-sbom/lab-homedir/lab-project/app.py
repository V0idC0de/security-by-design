import requests


request = requests.Request(
    "GET",
    "https://example.com/status",
    params={"service": "sbom-lab"},
).prepare()

print(f"Vorbereitete HTTP-Anfrage: {request.method} {request.url}")
print("Die Anfrage wird nicht gesendet. Es ist kein Netzwerkzugriff erforderlich.")