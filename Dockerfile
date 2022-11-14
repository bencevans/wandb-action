FROM python:3-slim
ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y gcc python3-dev
RUN pip install wandb

# FROM gcr.io/distroless/python3-debian10
# COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["python", "/app/main.py"]
