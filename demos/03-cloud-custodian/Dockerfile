FROM hashicorp/terraform:1.13

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

# Setze Berechtigungen für den Benutzer
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

# Installiere Google Cloud SDK/CLI
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86.tar.gz \
&& tar -xf google-cloud-cli-linux-x86.tar.gz \
&& rm google-cloud-cli-linux-x86.tar.gz \
&& mkdir -p /home/$USERNAME/.local \
&& mv google-cloud-sdk /home/$USERNAME/.local/gcloud \
&& /home/$USERNAME/.local/gcloud/install.sh --quiet --path-update true \
&& echo 'source /home/labuser/.local/gcloud/completion.bash.inc' >> /home/$USERNAME/.bashrc

# Installiere Cloud Custodian
RUN pipx ensurepath \
&& pipx install --quiet c7n \
&& pipx inject --quiet c7n c7n-gcp

ENTRYPOINT ["/bin/bash"]