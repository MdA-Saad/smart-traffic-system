FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# CRITICAL FOR 1-CORE VMs: Prevent PyTorch from spawning background threads
# If PyTorch spawns 4 threads on 1 core, context-switching will freeze the VM.
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1

RUN useradd -m appuser
WORKDIR /app

# Step 1: Install system dependencies required for OpenCV/PyTorch on barebones Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 2: Force PyTorch to install the CPU-only version (Saves ~2GB of space and massive RAM)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Step 3: Install Ultralytics (YOLO) without letting it overwrite our CPU PyTorch
RUN pip install --no-cache-dir ultralytics

COPY --chown=appuser:appuser detector.py .

USER appuser
CMD ["python", "detector.py"]
