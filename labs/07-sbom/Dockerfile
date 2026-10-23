FROM anchore/syft:v1.20.0@sha256:b46e597614ddc78621e560af3fabf9346e35462ea1c886a38b30bcc7ca601a73 AS sbom-tool
FROM anchore/grype:v0.110.0@sha256:af65fbc0c664691067788fe95ff88760b435543e45595eb2ca6f102fc476fbe1 AS scanner
FROM python:3.12.2-slim-bookworm@sha256:5dc6f84b5e97bfb0c90abfb7c55f3cacc2cb6687c8f920b64a833a2219875997

ARG USERNAME=labuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    mkdir -p /home/$USERNAME/lab-project && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME

ENV GRYPE_DB_CACHE_DIR=/opt/grype-db \
    GRYPE_DB_AUTO_UPDATE=false \
    GRYPE_DB_REQUIRE_UPDATE_CHECK=false \
    GRYPE_DB_VALIDATE_AGE=false \
    GRYPE_CHECK_FOR_APP_UPDATE=false \
    GRYPE_EXTERNAL_SOURCES_ENABLE=false \
    GRYPE_BY_CVE=true

COPY --from=scanner /grype /usr/local/bin/grype
RUN grype db import 'https://grype.anchore.io/databases/v6/vulnerability-db_v6.1.10_2026-10-21T00:30:22Z_1792650592.tar.zst?checksum=sha256%3A05c82f2ff6a19f149279374a8355cbcee55ea036d160fc2382f3b3d4de41006c' && \
    chmod -R a+rX /opt/grype-db

COPY --from=sbom-tool /syft /usr/local/bin/syft
ENV SYFT_CHECK_FOR_APP_UPDATE=false \
    SYFT_FILE_METADATA_SELECTION=none \
    SYFT_FORMAT_PRETTY=true \
    SYFT_SOURCE_NAME=sbom-lab \
    SYFT_SOURCE_VERSION=1.0.0

COPY debian.sources /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash-completion=1:2.11-6 bat=0.22.1-4 jq=1.6-2.1 less=590-2.1~deb12u2 \
        nano=7.2-1+deb12u1 tree=2.1.0-1 vim=2:9.0.1378-2 && \
    rm -rf /var/lib/apt/lists/*

COPY lab-homedir/lab-project/requirements.txt /home/$USERNAME/lab-project/requirements.txt
COPY constraints.txt /tmp/constraints.txt
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME /tmp/constraints.txt

USER $USERNAME
RUN python -m venv --without-pip /home/$USERNAME/lab-project/venv && \
    python -m pip --python /home/$USERNAME/lab-project/venv install --no-cache-dir \
        -r /home/$USERNAME/lab-project/requirements.txt \
        -c /tmp/constraints.txt && \
    rm /tmp/constraints.txt

USER root
COPY lab-homedir/ /home/$USERNAME/
COPY README.md /home/$USERNAME/GUIDE.md
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

USER $USERNAME
ENV PATH="/home/$USERNAME/lab-project/venv/bin:$PATH:/home/$USERNAME/.local/bin"
WORKDIR /home/$USERNAME
ENV TERM=xterm-color
RUN echo "alias guide='batcat /home/$USERNAME/GUIDE.md'" >> /home/$USERNAME/.bashrc

RUN printf "\nHISTCONTROL=\nHISTIGNORE=\nshopt -s histappend\nset -o history\nPROMPT_COMMAND='history -a'\n" >> /home/$USERNAME/.bashrc

ENTRYPOINT ["/bin/bash"]