# Sandboxed benchmark container: no inbound ports; outbound only to the model endpoint.
# docker build -t mcpguardbench .
# docker run --rm --network host -v $PWD/results:/app/results mcpguardbench \
#     python -m mcpguard.eval.run --config configs/smoke.yaml
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m bench && chown -R bench /app
USER bench
CMD ["python", "-m", "pytest", "-q"]
