FROM python:3.12-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Install dependencies only, not the project itself
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the source tree to preserve package structure
COPY . /app/src/

# Install the trending_server package
WORKDIR /app
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "trending_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
