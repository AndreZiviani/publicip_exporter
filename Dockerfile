FROM python:3.10.0-alpine3.13

WORKDIR /app

COPY src/. .

RUN adduser -D app && apk add --no-cache git
RUN pip install -r requirements.txt && \
    rm requirements.txt

RUN chown -R app:app /app

USER app

CMD ["python", "-u", "main.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${METRICS_PORT:=9798}/
