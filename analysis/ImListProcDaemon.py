import os
import json
import time

import gearman
from pymongo import MongoClient

from AnalyseImage import AnalyseImage

pid_file_name = "/var/run/iml.pid"
pid = os.getpid()
with open(pid_file_name, "wb") as pid_file:
    pid_file.write(str(pid))

mongo_client = None
mongo_db2 = None
mongo_collection2 = None

try:
    mongo_client = MongoClient()

    mongo_db2 = mongo_client['jobs']
    mongo_collection2 = mongo_db2['results']

except Exception as e:
    print e.message

cwd = os.path.dirname(os.path.realpath(__file__))#os.curdir
cascades_dir = os.path.join(cwd, "..", "extra", "cascades")

A = AnalyseImage(cascades_dir)


def gearman_listener(gearman_worker, gearman_job):
    data = json.loads(gearman_job.data)
    job_id = data['id']
    job_data = data['jobdata']
    images_list = job_data['images_list']
    print job_data

    for image in images_list:
        A.analyse_image(image['in_path'], image['out_path'])

    results_data = {}
    results_data['id'] = job_id
    results_data['result'] = {}
    results_data['ts_'] = int(time.time())

    mongo_collection2.insert(results_data)
    return "0"


gm_worker = gearman.GearmanWorker(['localhost:4730'])

gm_worker.register_task('ovrvue_imlproc', gearman_listener)

gm_worker.work()