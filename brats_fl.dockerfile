# FROM gramineproject/gramine:latest
FROM ubuntu:22.04

ENV GRAMINE=0

RUN apt update && apt install -y python3-pip \
    python3-venv \
    make \
    curl \
    lsb-release \
    vim

RUN curl -fsSLo /etc/apt/keyrings/gramine-keyring-$(lsb_release -sc).gpg https://packages.gramineproject.io/gramine-keyring-$(lsb_release -sc).gpg
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/gramine-keyring-$(lsb_release -sc).gpg] https://packages.gramineproject.io/ $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/gramine.list

RUN curl -fsSLo /etc/apt/keyrings/intel-sgx-deb.asc https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/intel-sgx-deb.asc] https://download.01.org/intel-sgx/sgx_repo/ubuntu $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/intel-sgx.list

RUN apt-get update && env DEBIAN_FRONTEND=noninteractive apt-get install -y gramine

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel

ENV PATH=/opt/venv/bin:$PATH

RUN mkdir /app

COPY requirements.txt /app/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

RUN fx experimental activate

COPY director /app/director
COPY fx.manifest.template /app/fx.manifest.template
COPY Makefile /app/Makefile

RUN echo '#!/bin/bash\n\
if [ "$GRAMINE" = "1" ]; then\n\
    exec gramine-sgx fx "$@"\n\
else\n\
    exec fx "$@"\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

RUN groupadd -r intel -g 1000 && \
    useradd -u 1000 -r -g intel -m -d /intel -c "intel" intel && \
    chmod 777 /intel

RUN chown -R intel:intel /app

RUN mkdir -p /intel/.metaflow/FederatedBrats && \
    chown -R intel:intel /intel/.metaflow/FederatedBrats

RUN rm -f /intel/.rnd

RUN echo -e 'http_proxy="http://proxy-dmz.intel.com:911/"\nhttps_proxy="http://proxy-dmz.intel.com:912/"' >> /etc/environment

USER intel

ENV HOME /intel

RUN fx experimental activate

RUN gramine-sgx-gen-private-key

RUN cd /app && make SGX=1

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]