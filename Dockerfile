FROM python:3.11.6-slim-bookworm as base

FROM base as builder

RUN apt-get update

RUN apt-get install -y --no-install-recommends gcc build-essential

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml /install/
COPY README.md /install/
COPY .python-version /install/

WORKDIR /install

RUN pip install .

FROM base

COPY --from=builder /opt/venv /opt/venv

COPY src/homework_bot /app/homework_bot
COPY .env /app/

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

CMD ["python", "-m", "homework_bot"]
