FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ENV PYTHONPATH=/workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from webdriver_manager.chrome import ChromeDriverManager; import shutil; shutil.copy(ChromeDriverManager().install(), '/usr/local/bin/chromedriver')"
RUN chmod +x /usr/local/bin/chromedriver

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]