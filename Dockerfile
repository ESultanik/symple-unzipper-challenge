FROM python:3.10

RUN mkdir /server && mkdir -p /server/static/etc

COPY *.py Dockerfile LICENSE README.md requirements.txt /server/
COPY static/etc/passwd /server/static/etc/

RUN tar czvf server.tar.gz server && mv server.tar.gz /server/static/

WORKDIR /server

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "--port", "80", "--host", "0.0.0.0", "server:app"]
