import wandb
import random

wandb.init(project="wandb-action")

for i in range(100):
    wandb.log({
      "epoch": i,
      "loss": random.random(),
    })

