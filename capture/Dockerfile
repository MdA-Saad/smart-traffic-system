FROM python:3.9-slim

# Prevent memory buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m appuser
WORKDIR /app

# Install headless OpenCV to avoid pulling 100MB+ of GUI libraries
RUN pip install --no-cache-dir opencv-python-headless==4.8.1.78

COPY --chown=appuser:appuser capture.py .

USER appuser
CMD ["python", "capture.py"]
