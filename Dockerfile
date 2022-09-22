FROM python:3.10-alpine
COPY . /app
WORKDIR /app
RUN pip install -r /app/requirements.txt

CMD ["python3", "-m", "mastoposter", "/config.ini"]
