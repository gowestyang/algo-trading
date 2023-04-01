FROM python:3.8-slim-buster
USER root

COPY main.py /

RUN pip install --upgrade pip
RUN pip install requests

CMD ["python", "/main.py"]
