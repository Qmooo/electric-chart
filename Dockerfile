FROM python:3.8-slim

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 30800

CMD ["python", "./ele.py"]