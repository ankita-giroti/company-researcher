FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome's official repo using the modern signed-by keyring method
RUN wget -q -O /usr/share/keyrings/google-chrome-keyring.gpg.tmp https://dl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /usr/share/keyrings/google-chrome-keyring.gpg.tmp \
    && rm /usr/share/keyrings/google-chrome-keyring.gpg.tmp \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Refresh apt sources AFTER adding the Chrome repo, then install Chrome + matching driver
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
