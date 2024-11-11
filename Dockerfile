FROM python:3.12.7-alpine AS base
WORKDIR /app

RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . .


FROM base AS production

CMD ["waitress-server", "wsgi:app"]


FROM base AS dev

CMD ["python", "app.py"]
