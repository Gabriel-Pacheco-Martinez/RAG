FROM python:3.11.10

WORKDIR /app

COPY requirements.txt .

# upgrade pip first
RUN pip install --upgrade pip

# install CPU-only PyTorch
RUN pip install torch==2.10.0+cpu --index-url https://download.pytorch.org/whl/cpu

# install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.cli", "-s"]