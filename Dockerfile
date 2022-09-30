FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt && rm /app/requirements.txt

COPY . /app

CMD ["python3", "-m", "mastoposter", "/config.ini"]
