# Jane test site. Build context: tests/fixtures/testsite
FROM python:3.12-slim
WORKDIR /app
COPY src/ /app/src/
ENV PYTHONPATH=/app/src PYTHONUNBUFFERED=1
RUN useradd --system --uid 10001 jane
USER jane
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/robots.txt', timeout=2)"]
CMD ["python", "-m", "jane_testsite", "--host", "0.0.0.0", "--port", "8080"]
