FROM python:3.9.6-alpine

WORKDIR /opt/backend

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add bash \
    postgresql-dev \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    vim \
    libressl-dev \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev \
    cargo \
    tzdata

RUN cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime
RUN echo "America/Sao_Paulo" >  /etc/timezone
ENV TZ America/Sao_Paulo
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod +x ./scripts/entrypoint.sh

RUN mkdir /opt/setup
RUN ln -s ./data/* /opt/setup/

ENTRYPOINT ["./scripts/entrypoint.sh"]
