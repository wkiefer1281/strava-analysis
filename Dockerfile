FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

# Set default environment variable for ADC
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/creds/servicecredentials.json"

CMD ["python", "main.py"]
