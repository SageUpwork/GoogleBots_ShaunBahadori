#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import json
import logging
import math
import os
from concurrent.futures import ThreadPoolExecutor

from mapBot import core
import pandas as pd
import random
def loggerInit(logFileName):
    try:
        os.makedirs("logs")
    except:
        pass
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler = logging.FileHandler(f'logs/{logFileName}')
    # file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # stream_handler.setLevel(logging.ERROR)
    logger.addHandler(stream_handler)
    return logger


logger = loggerInit(logFileName="backlink.googleBot.log")


if __name__ == '__main__':

    parallelWorkerCount = 5
    print("Is this first run today? [Y/N]")
    freshCheck = input()
    df= pd.read_csv('mapRun_Queue.csv')
    queueData = df.transpose().to_dict()
    if freshCheck == "Y":
        df["completedCount"] = 0
        df.to_csv('mapRun_Queue.csv', index=False)
        core(queueData, parallelWorkerCount, df)
    elif freshCheck == "N":
        core(queueData, parallelWorkerCount, df)
    else:
        logger.debug("Invalid reply. Please restart app")

