# Image um die .bashrc zu kopieren
FROM ubuntu:noble@sha256:59a458b76b4e8896031cd559576eac7d6cb53a69b38ba819fb26518536368d86 AS ubuntu

# Haupt-Image
FROM hashicorp/terraform:1.13@sha256:dfb1889a8ee74ada3ddacc48f89b8a0d69f3e114de3d8a2ce15f6a8d3dbfdbe2

# Installiere grundlegende Pakete
RUN apk add --no-cache less nano vim bat busybox-extras shadow bash curl jq yq \
&& ln -s "$(which bat)" "$(dirname $(which bat))/batcat"
RUN apk add --no-cache python3 pipx

# Erstelle einen nicht-root Benutzer
ARG USERNAME=labuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Füge einen non-root User hinzu
RUN groupadd -g $USER_GID $USERNAME && useradd -m -u $USER_UID -g $USER_GID $USERNAME

# Übertrage Demo-Dateien
COPY ./terraform /home/$USERNAME/terraform
COPY ./policies /home/$USERNAME/policies

# Kopiere .bashrc aus dem ubuntu-Image
COPY --from=ubuntu /root/.bashrc /home/$USERNAME/.bashrc

# Setze Berechtigungen für den Benutzer
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME
ENV TERM=xterm-color

# Installiere Google Cloud SDK/CLI
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86.tar.gz \
&& tar -xf google-cloud-cli-linux-x86.tar.gz \
&& rm google-cloud-cli-linux-x86.tar.gz \
&& mkdir -p /home/$USERNAME/.local \
&& mv google-cloud-sdk /home/$USERNAME/.local/gcloud \
&& /home/$USERNAME/.local/gcloud/install.sh --quiet --path-update true

# Aktiviere Bash-Vervollständigung für Terraform und gcloud
RUN terraform -install-autocomplete
RUN echo 'source /home/labuser/.local/gcloud/completion.bash.inc' >> /home/$USERNAME/.bashrc

# Installiere Cloud Custodian
RUN pipx ensurepath \
&& pipx install --quiet c7n \
&& pipx inject --quiet c7n c7n-gcp

# Schreibe Hinweis auf Guide in GUIDE.md
RUN echo "Dokumentation unter https://github.com/V0idC0de/security-by-design/tree/main/demos/05-cloud-custodian" > /home/$USERNAME/GUIDE.md

ENTRYPOINT ["/bin/bash"]