FROM python:3-slim


RUN apt-get update && apt-get install -y gcc python3-dev github
RUN pip install wandb

ADD . /app

WORKDIR /app
ENV PYTHONPATH /app
CMD ["python", "/app/main.py"]
