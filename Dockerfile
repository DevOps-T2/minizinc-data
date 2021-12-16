FROM python:3.9

COPY /src /src

COPY /src/requirements.txt /src

WORKDIR /src

RUN pip install -r requirements.txt

CMD uvicorn --host 0.0.0.0 --port 80 app:app

EXPOSE 80
