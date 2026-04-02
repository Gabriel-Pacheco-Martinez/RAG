FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Upgrade pip first
RUN pip install --upgrade pip

# Install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.session_expiry_listener"]

