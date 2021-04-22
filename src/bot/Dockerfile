FROM python:latest

ENV TZ Europe/Moscow
WORKDIR /bot
VOLUME [ "/src/bot/logs/" ]

COPY ./requirements.txt /bot
RUN pip install -r requirements.txt

COPY . /bot

CMD ["python3", "bot.py"]