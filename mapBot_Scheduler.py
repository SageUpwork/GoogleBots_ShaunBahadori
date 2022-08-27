import os
import time
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler

from mapBot import core


def mainRun():
    parallelWorkerCount = 5
    df = pd.read_csv('mapRun_Queue.csv')
    df.fillna(0)
    queueData = df.transpose().to_dict()
    df["completedCount"] = 0
    df.to_csv('mapRun_Queue.csv', index=False)
    core(queueData, parallelWorkerCount, df)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(mainRun, 'cron', hour= 5, minute= 0, max_instances=1)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()







