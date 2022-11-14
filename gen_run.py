import wandb
import random
import os

wandb.init(project="wandb-action")

for i in range(100):
    wandb.log(
        {
            "epoch": i,
            "loss": random.random(),
        }
    )
