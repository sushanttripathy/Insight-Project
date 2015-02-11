__author__ = 'Sushant'
import os
import json
import time

import gearman
from pymongo import MongoClient

from AnalyseURL import AnalyseURL

pid_file_name = "/var/run/au.pid"
pid = os.getpid()
with open(pid_file_name, "wb") as pid_file:
    pid_file.write(str(pid))

mongo_client = None
mongo_db2 = None
mongo_collection2 = None

mongo_db3 = None
mongo_collection3 = None

cache_window = 5*3600



try:
    mongo_client = MongoClient()

    mongo_db2 = mongo_client['jobs']
    mongo_collection2 = mongo_db2['results']

    mongo_db3 = mongo_client['pre_classified']
    mongo_collection3 = mongo_db3['results']

except Exception as e:
    print e.message

cwd = os.path.dirname(os.path.realpath(__file__)) #os.curdir
classifier_path = os.path.join(cwd, "..", "extra", "classifiers", "text", "mnb.pkl")
cascades_dir = os.path.join(cwd, "..", "extra", "cascades")

A = AnalyseURL(classifier_path, cascades_dir)


def gearman_listener(gearman_worker, gearman_job):
    data = json.loads(gearman_job.data)
    job_id = data['id']
    job_data = data['jobdata']
    url = job_data['url']
    request_time = time.time()
    print job_data

    #check if the URL is pre-classified and the classification is within 2 hours old
    try:
        result = mongo_collection3.find_one({'url':url, "ts": {"$gte": time.time() - cache_window}})
        if result is not None and result['ts'] > (request_time - cache_window):
            results_data = {}
            results_data['id'] = job_id
            results_data['result'] = result['result']['result']
            results_data['ts_'] = int(time.time())
            mongo_collection2.insert(results_data)
            return "0"
    except Exception as e:
        print e.message

    res = A.analyse_url(url)
    print res
    results_data = {}

    results_data['id'] = job_id
    results_data['result'] = res
    results_data['ts_'] = int(time.time())

    mongo_collection2.insert(results_data)

    cache_data = {}
    cache_data['ts'] = time.time()
    cache_data['url'] = url
    cache_data['result'] = results_data
    mongo_collection3.insert(cache_data)
    return "0"


gm_worker = gearman.GearmanWorker(['localhost:4730'])

gm_worker.register_task('ovrvue_urlproc', gearman_listener)

gm_worker.work()