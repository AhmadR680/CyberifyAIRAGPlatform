FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt .

# Ensure OS packages are up-to-date to address known vulnerabilities
RUN set -eux \
	&& apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y --no-install-recommends ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000