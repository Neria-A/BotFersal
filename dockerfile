FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERD 1

LABEL Maintainer="your name"

WORKDIR /home/orangepi/BotFersal

COPY *.py requirements.txt  ./

WORKDIR /home/orangepi/BotFersal
RUN apt-get update
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r /home/orangepi/BotFersal/requirements.txt

ENV PYTHONPATH /home/orangepi/BotFersal

CMD [ "python3", "./bot_fersal.py"]