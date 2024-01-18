FROM python:3.10.13-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN addgroup --gid 1000 app &&\     
    adduser --home /app --uid 1000 --gid 1000 app &&\
    mkdir -p /app

WORKDIR /app

COPY . .

RUN chown -R app:app /app

USER app

RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip &&\
    python3 -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt

ENTRYPOINT [ "python3", "-m", "gunicorn", "-b", "0.0.0.0:8080", "--workers", "2", "bood.wsgi", "--reload" ]
