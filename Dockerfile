FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    wget \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    libxtst6 \
    libxi6 \
    xfonts-75dpi \
    xfonts-base \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf from official GitHub releases
# python:3.9-slim is based on Debian 11 (bullseye)
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb -O /tmp/wkhtmltox.deb \
    && apt-get update \
    && dpkg -i /tmp/wkhtmltox.deb || apt-get install -yf \
    && rm /tmp/wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
# Default command uses startup script which handles PORT correctly
CMD ["./start.sh"] 