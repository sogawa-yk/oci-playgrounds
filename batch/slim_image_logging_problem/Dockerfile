# ベースイメージ
FROM python:3.9-slim

RUN pip install oci
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY main.py .
RUN chown -R appuser:appuser /app
ENV PYTHONUNBUFFERED=1
USER 1000
CMD ["python", "main.py"]