FROM python:3.8-slim-buster
USER root

COPY src /src
COPY main.py /
COPY requirements.txt /
COPY btoandav20-0.2.1-py3-none-any.whl /

#RUN apt-get update \
#&& apt-get install -y --no-install-recommends git \
#&& apt-get purge -y --auto-remove \
#&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN pip install git+https://github.com/happydasch/btoandav20
RUN pip install btoandav20-0.2.1-py3-none-any.whl

CMD ["python", "/main.py"]
