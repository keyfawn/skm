import logging
import os

logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)


def get_logger(name):
    if not os.path.isdir('logs'):
        os.mkdir('logs')

    logging.basicConfig(
        level=logging.INFO,
        force=True,
        format="%(asctime)s | %(levelname)s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s",
        handlers=[
            logging.FileHandler(f"logs/{name}.log"),
            logging.StreamHandler()])
