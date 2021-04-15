FROM python:latest

ENV TZ Europe/Moscow
WORKDIR /bot
VOLUME [ "/src/bot/logs/" ]

COPY . /bot
RUN pip install -r requirements.txt

CMD ["python3", "bot.py"]