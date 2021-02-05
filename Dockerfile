### 1. Get Linux
FROM python:alpine

### 2. Get Java via the package manager
RUN apk update \
    && apk upgrade \
    && apk add --no-cache \
    openjdk8-jre \
    gcc \
    libc-dev \
    musl-dev \
    linux-headers \
    python2-dev

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"
