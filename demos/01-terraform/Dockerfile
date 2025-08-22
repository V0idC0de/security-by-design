FROM hashicorp/terraform:1.13

# Installiere grundlegende Pakete
RUN apk add --no-cache less nano vim busybox-extras jq shadow bash

# Erstelle einen nicht-root Benutzer
ARG USERNAME=labuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Füge einen non-root User hinzu
RUN groupadd -g $USER_GID $USERNAME && useradd -m -u $USER_UID -g $USER_GID $USERNAME

# Übertrage Demo-Dateien
COPY ./workspace /home/$USERNAME/terraform

# Setze Berechtigungen für den Benutzer
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME/terraform

ENTRYPOINT ["/bin/bash"]