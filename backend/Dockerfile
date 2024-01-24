FROM python:3.11.2-alpine3.17
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install gunicorn==20.1.0
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:7070" ]