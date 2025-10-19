FROM ubuntu:noble@sha256:59a458b76b4e8896031cd559576eac7d6cb53a69b38ba819fb26518536368d86

# Installiere git und weitere benötigte Tools
RUN apt-get update && \
    apt-get install -y git tree nano vim wget sudo bash-completion jq yq

# Erstelle einen nicht-root Benutzer
ARG USERNAME=labuser
ARG USER_UID=1001
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Installiere GitHub CLI
RUN (type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
    && sudo mkdir -p -m 755 /etc/apt/keyrings \
    && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt update \
    && sudo apt install gh -y

# Entferne Paketlisten
RUN rm -rf /var/lib/apt/lists/*

# Aktiviere Bash-Vervollständigung für GitHub CLI
RUN echo 'eval "$(gh completion -s bash)"' >> /home/$USERNAME/.bashrc

# Übertrage Demo-Dateien
COPY ./lab-id-tokens /home/$USERNAME/lab-id-tokens

# Setze Berechtigungen für den Benutzer
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

USER $USERNAME

# Bereit Repository für Push vor
WORKDIR /home/$USERNAME/lab-id-tokens
RUN git config --global user.name "labuser" && \
    git config --global user.email "labuser@id-tokens.lab" && \
    git init && \
    git add . && \
    git commit -m "Initial commit"

WORKDIR /home/$USERNAME
ENV TERM=xterm-color

ENTRYPOINT ["/bin/bash"]