FROM python:3-alpine
WORKDIR /app
COPY requirements.txt ./
RUN apk add --virtual .build-deps --no-cache \
        libressl-dev \
        libxslt-dev \
        libffi-dev \
        build-base && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps
COPY . /app
CMD [ "python", "main.py", "daemon" ]