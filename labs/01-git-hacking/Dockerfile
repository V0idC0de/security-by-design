FROM python:3.12.2-slim-bookworm@sha256:5dc6f84b5e97bfb0c90abfb7c55f3cacc2cb6687c8f920b64a833a2219875997

ARG TRUFFLEHOG_VERSION=v3.90.5
ARG GITHACKER_VERSION=1.1.7
ARG BANDIT_VERSION=1.8.6
ARG WEBSERVER_PATH=/lab-webserver

# Installiere git und weitere benötigte Tools
RUN apt-get update && \
    apt-get install -y git nano vim bat jq curl wget bash-completion && \
    rm -rf /var/lib/apt/lists/*

COPY lab-webserver $WEBSERVER_PATH

# Erstelle einen nicht-root Benutzer
ARG USERNAME=labuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME $WEBSERVER_PATH

USER $USERNAME
# Setze $PATH, sodass pip-Tools (hier "pre-commit") korrekt gefunden werden
ENV PATH="$PATH:/home/$USERNAME/.local/bin"

# Installiere TruffleHog
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh \
    | sh -s -- -b /home/$USERNAME/.local/bin $TRUFFLEHOG_VERSION

# Installiere githacker und Bandit
RUN pip install GitHacker==$GITHACKER_VERSION bandit==$BANDIT_VERSION

WORKDIR $WEBSERVER_PATH/webroot
RUN git init && \
git config user.name "TheD3V" && \
git config user.email "thedev@example.com" && \
git add . && \
git commit -m "Initial commit"

# Simuliere etwas Git History
RUN bash $WEBSERVER_PATH/commit-generator.sh $WEBSERVER_PATH/webroot/config/db.json

WORKDIR /home/$USERNAME
ENV TERM=xterm-color

# ARGs können in ENTRYPOINTs nicht gut verwendet werden - daher nochmal als ENV
ENV WEBSERVER_PATH=$WEBSERVER_PATH

# Schreibe Hinweis auf Guide in GUIDE.md
RUN echo "Dokumentation unter https://github.com/V0idC0de/security-by-design/tree/main/labs/01-git-hacking" > /home/$USERNAME/GUIDE.md
# Setze Alias zum schnellen Anzeigen des Doku-Links
RUN echo "alias guide='cat /home/$USERNAME/GUIDE.md'" >> /home/$USERNAME/.bashrc

# Starte Webserver + Shell
ENTRYPOINT ["/bin/bash", "-c", "python ${WEBSERVER_PATH}/server.py 2>&1 > ${WEBSERVER_PATH}/server.log & exec bash"]
