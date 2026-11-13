# Read-along: never built in this course. The build context is the service's repository root.
FROM python:3.14.7-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.14.7-slim
RUN useradd --system --no-create-home --home-dir /srv/app --uid 10001 solver \
 && mkdir -p /srv/data && chown solver /srv/data
COPY --from=build /install /usr/local
WORKDIR /srv/app
COPY src/ ./
USER solver
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["fastapi", "run", "job_api.py", "--port", "8000"]
