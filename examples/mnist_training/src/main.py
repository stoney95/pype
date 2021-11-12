from pypely import pipeline, fork, to, merge
from pypely.memory import memorizable


import torch
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
from datetime import datetime

from mnist_training.src.ds.dataset import create_dataloader
from mnist_training.src.ds.models import create_linear_net
from mnist_training.src.ds.tracking import ExperimentTracker
from mnist_training.src.ds.training import TrainingDependencies
from mnist_training.src.ds.run.epoch import run_epochs, EpochData
from mnist_training.src.output import log_metrics, print_summary
import mnist_training.src.ds.tensorboard as tb_tracking

LR = 5e-5
OPTIMIZER = torch.optim.Adam
EPOCHS = 20
BATCH_SIZE = 128

HERE = Path(__file__).parent.resolve()
LOG_DIR = HERE.parent.parent.parent / "runs" / datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

DATA_DIR = HERE.parent / "data"
TRAIN_DATA = DATA_DIR / "train-images-idx3-ubyte.gz"
TRAIN_LABELS = DATA_DIR / "train-labels-idx1-ubyte.gz"
TEST_DATA = DATA_DIR / "t10k-images-idx3-ubyte.gz"
TEST_LABELS = DATA_DIR / "t10k-labels-idx1-ubyte.gz"


create_training_dependencies = pipeline(
    fork(
        create_linear_net(OPTIMIZER, LR),
        lambda: torch.nn.CrossEntropyLoss(reduction="mean"),
        lambda: ExperimentTracker[SummaryWriter](SummaryWriter(log_dir=str(LOG_DIR)), tb_tracking.flush, tb_tracking.add_batch_metric, tb_tracking.add_epoch_metric, tb_tracking.add_epoch_confusion_matrix),
    ),
    to(TrainingDependencies)
)


create_epoch_data = pipeline(
    fork(
        lambda: create_dataloader(BATCH_SIZE, TRAIN_DATA, TRAIN_LABELS),
        lambda: create_dataloader(BATCH_SIZE, TEST_DATA, TEST_LABELS),
    ),
    to(EpochData)
)


log_epoch =fork(
    log_metrics,
    print_summary(EPOCHS)
)


log_epochs = lambda epochs, training_dependencies: [log_epoch(epoch, i, training_dependencies) for i, epoch in enumerate(epochs)]


def main():
    _create_training_dependencies = memorizable(create_training_dependencies)
    _log_epochs = memorizable(log_epochs)
    _run_epochs = run_epochs(EPOCHS)

    run = pipeline(
        fork(
            _create_training_dependencies >> "training_dependencies",
            create_epoch_data
        ),
        merge(_run_epochs),
        _log_epochs << "training_dependencies"
    )

    run()

if __name__ == '__main__':
    main()