FROM python:3.10-slim


RUN apt-get update && apt-get install -y gcc python3-dev
RUN pip install wandb github

ADD . /app

WORKDIR /app
ENV PYTHONPATH /app
CMD ["python", "/app/main.py"]
