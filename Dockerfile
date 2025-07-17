FROM python:3.13
LABEL authors="Daniel Svitan"

WORKDIR /app
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 manage.py migrate
RUN pip3 install daphne

EXPOSE 8000
ENTRYPOINT ["daphne", "api.asgi:application", "--bind", "0.0.0.0"]
