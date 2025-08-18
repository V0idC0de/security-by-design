# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Installiere git und weitere benötigte Tools
RUN apt-get update && \
    apt-get install -y git nano vim tree bat && \
    rm -rf /var/lib/apt/lists/*

# Erstelle einen nicht-root Benutzer
ARG USERNAME=labuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Kopiere lab-metadata, mit Konfigurationen und Dateien für das Lab
COPY lab-metadata/ /home/$USERNAME/

# Kopiere den Lab-Inhalt ins Home-Verzeichnis des Benutzers
COPY lab-repository/ /home/$USERNAME/lab-repository

# Setze Berechtigungen für den Benutzer
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

# Arbeite im Folgenden als nicht-root Benutzer
USER $USERNAME
# Setze $PATH, sodass pip-Tools korrekt gefunden werden
ENV PATH="$PATH:/home/$USERNAME/.local/bin"

# Schreibe einen Commit in die Historie und entferne das Secret aus README.md
# `git` wurde durch das Kopieren der `lab-metadata` bereits konfiguriert
WORKDIR /home/$USERNAME/lab-repository
RUN git init && \
    git add .gitignore && \
    git commit -m 'Initial Commit'

# Setze Working Directory als Home-Verzeichnis des Benutzers
WORKDIR /home/$USERNAME

CMD ["/bin/bash"]
