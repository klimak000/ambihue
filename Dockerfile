#
# Addon Base Image with Python3 preinstalled:
#   https://github.com/hassio-addons/addon-base-python
#   14.0.4 is the newest version with Python <= 3.12
#
ARG BUILD_FROM
FROM ${BUILD_FROM:-ghcr.io/hassio-addons/base-python:14.0.4} AS build_base

# Disable warning and install Python packages on system level: PEP668
ENV PIP_BREAK_SYSTEM_PACKAGES=1

ARG TARGETPLATFORM
RUN echo "Building for platform: $TARGETPLATFORM"

# Install mbedtls-dev manually for some platforms
#   some platforms require to build wheel for python-mbedtls
#   https://github.com/Mbed-TLS/mbedtls
#   https://dl-cdn.alpinelinux.org/alpine/v3.16/main/aarch64/
#   can takes up to 15 minutes to build
#   Steps:
#   1. Install musl-1.2.5-r1 as build-base dependency
#   2. Install build-base as build wheel dependency
#   3. Install mbedtls-dev=2.28.8-r0 as python-mbedtls=2.10.1 dependency

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ] || [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
    echo "http://dl-cdn.alpinelinux.org/alpine/v3.16/main" >> /etc/apk/repositories && \
    apk update && \
    apk add --no-cache musl=1.2.5-r1 && \
    apk add --no-cache build-base=0.5-r3 && \
    apk add --no-cache mbedtls-dev=2.28.8-r0 && \
    pip install --no-cache-dir python-mbedtls==2.10.1; \
    else \
    echo "Skipping for $TARGETPLATFORM"; \
    fi

# Copy data for add-on
COPY requirements.txt /

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

#
# Linters stage to test Python code - not build by default
#
FROM build_base AS linters

# Copy data for add-on
COPY .github/requirements_dev.txt /

# Install dependencies
RUN pip install --no-cache-dir -r requirements_dev.txt

# Copy AmbiHue # sync with 72-73
COPY src /src
COPY ambihue.py pyproject.toml /

RUN isort src ambihue.py \
    && black src ambihue.py \
    && mypy src \
    && mypy ambihue.py

# Copy data for add-on
COPY .github/linters/.python-lint /
RUN pylint ambihue ambihue.py

#
# Final stage used by Home Assistant Addon supervisor based on `build_base`
#
FROM build_base AS final

# Copy AmbiHue # sync with 54-55
COPY src /src
COPY ambihue.py pyproject.toml /

# Install AmbiHue
RUN pip install --no-cache-dir .

CMD [ "/ambihue.py" ]

# Labels
LABEL \
    io.hass.name="ambihue" \
    io.hass.arch="$TARGETPLATFORM" \
    io.hass.type="addon" \
    io.hass.version="1.0.1" \
    maintainer="klimak000"
