# Image um die .bashrc zu kopieren
FROM ubuntu:noble@sha256:59a458b76b4e8896031cd559576eac7d6cb53a69b38ba819fb26518536368d86 AS ubuntu

FROM hashicorp/terraform:1.13@sha256:dfb1889a8ee74ada3ddacc48f89b8a0d69f3e114de3d8a2ce15f6a8d3dbfdbe2

# Installiere grundlegende Pakete
RUN apk add --no-cache less nano vim bat busybox-extras shadow bash bash-completion curl jq yq github-cli \
&& ln -s "$(which bat)" "$(dirname $(which bat))/batcat"

# Erstelle einen nicht-root Benutzer
ARG USERNAME=labuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Füge einen non-root User hinzu
RUN groupadd -g $USER_GID $USERNAME && useradd -m -u $USER_UID -g $USER_GID $USERNAME

# Übertrage Demo-Dateien
COPY ./terraform /home/$USERNAME/terraform

# Kopiere .bashrc aus dem ubuntu-Image
COPY --from=ubuntu /root/.bashrc /home/$USERNAME/.bashrc

# Setze Berechtigungen für den Benutzer
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME
ENV TERM=xterm-color

# Aktiviere Bash-Vervollständigung für GitHub CLI und Terraform
RUN echo 'eval "$(gh completion -s bash)"' >> /home/$USERNAME/.bashrc
RUN terraform -install-autocomplete

ENTRYPOINT ["/bin/bash"]