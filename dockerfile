FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERD 1

LABEL Maintainer="neria.amsalem"

WORKDIR /home/ubuntu/BotFersal

COPY *.py requirements.txt ./

WORKDIR /home/ubuntu/BotFersal
RUN apt-get update
RUN apt-get -y install cron
RUN pip3 install --upgrade pip
RUN pip3 install -r /home/ubuntu/BotFersal/requirements.txt
RUN pip3 install pyTelegramBotAPI

ENV PYTHONPATH /home/ubuntu//BotFersal

CMD [ "python3", "./bot_fersal.py"]