FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERD 1

LABEL Maintainer="neria.amsalem"

WORKDIR /home/ubuntu/BotFersal

COPY *.py requirements.txt  ./

WORKDIR /home/ubuntu/BotFersal
RUN apt-get update
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r /home/ubuntu/BotFersal/requirements.txt
#RUN pip3 install pyTelegramBotAPI
#RUN pip3 install pymongo
#RUN pip3 install python-barcode
#RUN pip3 install python-imap
#RUN pip3 install Pillow
#RUN pip3 install email
#RUN pip3 install regex
#RUN pip3 install jsonlib

ENV PYTHONPATH /home/ubuntu/BotFersal

CMD [ "python3", "./bot_fersal.py"]