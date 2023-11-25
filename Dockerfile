FROM python:3.11.6

WORKDIR /app

COPY src/homework_bot /app/src/homework_bot
COPY .env /app/
COPY pyproject.toml /app/
COPY README.md /app/
COPY .python-version /app/

RUN pip install --no-cache-dir .

CMD ["python", "src/homework_bot/main.py"]
