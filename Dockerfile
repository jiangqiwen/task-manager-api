FROM docker.m.daocloud.io/library/python:3.11-slim AS builder
WORKDIR /build

ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com
    
COPY src/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM docker.m.daocloud.io/library/python:3.11-slim AS runtime
ENV PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.11/site-packages"
    
WORKDIR /app
COPY --from=builder /install /install
COPY src/ .
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app /install
USER appuser
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]