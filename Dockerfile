FROM python:3.11-slim

LABEL maintainer="brn.madeira@gmail.com"
LABEL description="MdMax - Compress files by 79.7% + track token economy"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[all]"

# Create config directory
RUN mkdir -p ~/.mdmax

# Set entry point
ENTRYPOINT ["mdmax"]
CMD ["--help"]
