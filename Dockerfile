FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ovh_db_backup ovh_db_backup

CMD ["python", "-m", "ovh_db_backup"]
