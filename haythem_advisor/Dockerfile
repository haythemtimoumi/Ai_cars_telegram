FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libpq-dev \
    gcc \
    curl \
    xz-utils \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libgtk-3-0 \
    libx11-xcb1 \
    libasound2 \
    libgbm1 \
    libvulkan1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome (specific version that we know has matching Chromedriver)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable=135.0.7049.95-1 \
    && rm -rf /var/lib/apt/lists/*

# Install matching Chromedriver (exact version)
RUN wget -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.95/linux64/chromedriver-linux64.zip \
    && unzip chromedriver.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver.zip chromedriver-linux64

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]