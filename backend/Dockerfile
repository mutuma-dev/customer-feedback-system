# Recipe for the backend container image.

# 1) Start from an image that already has Python installed ("slim" = small).
FROM python:3.14-slim

# 2) Work inside /srv in the container.
WORKDIR /srv

# 3) Do not write .pyc files; print logs immediately instead of buffering them.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 4) Copy ONLY the dependency list first and install it. Docker caches this step, so
#    rebuilds are fast unless requirements.txt changed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Now copy the application code (.dockerignore keeps secrets and tests out).
COPY . .

# 6) Document that the app listens on port 8000.
EXPOSE 8000

# 7) On start: create/upgrade the database tables, then run the API server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
