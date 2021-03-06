FROM python:3.8-slim-buster

EXPOSE 5000

ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=flaskr/main.py
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development
COPY requirements.txt .
RUN pip3 install -r requirements.txt
WORKDIR /code
ENV PYTHONPATH=/code
COPY . .

ENTRYPOINT [ "python3", "flaskr/main.py" ]