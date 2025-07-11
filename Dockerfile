FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic/ /app/alembic/
COPY bot/ /app/bot/
COPY alembic.ini main.py /app/

CMD ["sh", "-c", "alembic upgrade head && python main.py"]