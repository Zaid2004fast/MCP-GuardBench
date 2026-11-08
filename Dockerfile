# MCPGuardBench - sandboxed benchmark container.
# No inbound ports; the only outbound traffic is to the model endpoint you configure.
#
#   docker build -t mcpguardbench .
#   docker run --rm mcpguardbench                                   # unit + end-to-end tests
#   docker run --rm -v "$PWD/results:/app/results" mcpguardbench \
#       python experiments/reproduce.py reference report            # LLM-free experiments
#   docker compose up                                               # with a local Ollama (see compose file)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir --no-deps -e . \
 && useradd -m bench && chown -R bench /app
USER bench
CMD ["python", "-m", "pytest", "-q"]
