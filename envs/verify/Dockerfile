FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port 8080 (required by specification)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV HOST=0.0.0.0

# Resource limits (documented - enforced by orchestrator)
# CPU: 8 cores maximum
# GPU: 24GB VRAM (NVIDIA GPU with CUDA support)
# RAM: 32GB maximum
# Storage: 500GB maximum

# Network restrictions:
# NO direct internet access from container
# Access to designated search API only (via internal network)
# All LLM weights must be bundled in container or downloaded during build

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
