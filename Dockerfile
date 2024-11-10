FROM python:3.12.7-alpine AS production

WORKDIR /app
ARG PORT="8080"

RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . .

EXPOSE $PORT

CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "$PORT", "app:app"]


FROM python:3.12.7-alpine AS dev

WORKDIR /app
ARG PORT="5000"

RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . .

EXPOSE $PORT

CMD ["flask", "run", "--debug", "--host", "0.0.0.0", "--port", "$PORT"]
