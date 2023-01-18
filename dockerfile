FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERD 1

LABEL Maintainer="your name"

WORKDIR <insert path>

COPY *.py requirements.txt  ./

WORKDIR <insert path>
RUN apt-get update
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r <insert path>/requirements.txt

ENV PYTHONPATH <insert path>

CMD [ "python3", "./bot_fersal.py"]