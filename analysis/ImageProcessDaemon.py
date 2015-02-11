#!/usr/bin/python
__author__ = 'Sushant'

import threading
import os
import tempfile
import hashlib
import time
import json
import pprint

import gearman
from pymongo import MongoClient

from CloudFiles import CloudFiles
from ImageFeatureDetect import ImageROI, ImageFeatureDetect, Image
from ThreadPool import ThreadPool


pid_file_name = "/var/run/ipd.pid"
pid = os.getpid()
with open(pid_file_name, "wb") as pid_file:
    pid_file.write(str(pid))

# Load cascades

feature_detectors = []
cloud_files_con = []
locks = []

mongo_lock = threading.Lock()

try:
    mongo_client = MongoClient()

    mongo_db = mongo_client['ovrvue']
    mongo_collection = mongo_db['images']

    mongo_db2 = mongo_client['jobs']
    mongo_collection2 = mongo_db2['results']
    """
    element = {
        "field1":"value1",
        "field2":"value2",
        "field3":"value3"
    }
    collection.insert(element)
    client.close()
    """
except Exception as e:
    print e.message

for i in range(0, 8):
    print "Starting worker thread : " + str(i)
    ifd = ImageFeatureDetect()
    cwd = os.path.dirname(os.path.realpath(__file__)) #os.path.curdir

    cascade_dir = os.path.join(cwd, "..", "extra", "cascades")

    face_cascade_1 = os.path.join(cascade_dir, "face", "haarcascade_frontalface_alt_tree.xml")
    #face_cascade_2 = os.path.join(cascade_dir, "face", "haarcascade_profileface.xml")
    #face_cascade_2 = os.path.join(cascade_dir, "face", "lbpcascade_frontalface.xml")
    face_cascade_2 = os.path.join(cascade_dir, "face", "haarcascade_frontalface_alt.xml")
    face_cascade_3 = os.path.join(cascade_dir, "face", "hogcascade_face_24x24_d3_s17.xml")

    breast_cascade_1 = os.path.join(cascade_dir, "breast", "haarcascade_breast.xml")
    breast_cascade_2 = os.path.join(cascade_dir, "breast", "hogcascade_breasts_36x36-d3_1_17.xml")

    bikini_top_cascade = os.path.join(cascade_dir, "bikini_top", "haarcascade_bikinitop_24x24_d2_s21.xml")

    midriff_cascade = os.path.join(cascade_dir, "midriff", "hogcascade_midriff_36x36-d3_1_17.xml")

    mons_pubis_cascade = os.path.join(cascade_dir, "mons_pubis", "hogcascade_32x32_d3_s11.xml")

    ifd.load_cascade(face_cascade_1)
    ifd.load_cascade(face_cascade_2)
    ifd.load_cascade(face_cascade_3)

    ifd.load_cascade(breast_cascade_1)
    ifd.load_cascade(breast_cascade_2)

    ifd.load_cascade(bikini_top_cascade)

    ifd.load_cascade(midriff_cascade)

    ifd.load_cascade(mons_pubis_cascade)

    feature_detectors.append(ifd)

    cf = CloudFiles()

    cloud_files_con.append(cf)

    lock = threading.Lock()

    locks.append(lock)


def thread_func(lock, ifd, cloud_files_obj, src_container_name, cloud_image_path, dest_container_name, job_id, image_id,
                image_ts):
    lock.acquire()
    nosql_data = {}

    nosql_data['approved'] = 1

    # cloud_files_obj = CloudFiles()

    cloud_files_obj.set_container(src_container_name)
    _, file_extension = os.path.splitext(cloud_image_path)

    temp_dir = tempfile.gettempdir()

    m = hashlib.md5(repr(image_id))

    temp_name = m.hexdigest() + "x" +repr(image_id) + file_extension

    m.update("proc")
    temp_proc_name = m.hexdigest() + "x" +repr(image_id) + ".jpg"#file_extension

    m.update("thumb")
    temp_proc_thumb_name = m.hexdigest() + "x" +repr(image_id) + ".jpg"#file_extension

    m.update("cens")
    temp_cens_name = m.hexdigest() + "x" +repr(image_id) + ".jpg"#file_extension

    m.update("thumb")
    temp_cens_thumb_name = m.hexdigest() + "x" +repr(image_id) + ".jpg"#file_extension

    temp_path = os.path.join(temp_dir, temp_name)

    pprint.pprint(cloud_files_obj)

    print "Downloading image " + cloud_image_path + " in " + src_container_name + " to " + temp_path
    cloud_files_obj.download_file(cloud_image_path, temp_path)
    if os.path.isfile(temp_path):
        print "File successfully downloaded!"
    else:
        print "File not found!"

    ifd.load_image(temp_path)
    ifd.resize_image(800, 800)

    temp_proc_path = os.path.join(temp_dir, temp_proc_name)

    print "Saving file to " + temp_proc_path
    ifd.save_image(temp_proc_path)
    if os.path.isfile(temp_proc_path):
        print "File successfully saved!"
    else:
        print "File not found!"

    cloud_files_obj.set_container(dest_container_name)

    cloud_files_obj.upload_file(temp_proc_path, temp_proc_name)

    temp_proc_thumb_path = os.path.join(temp_dir, temp_proc_thumb_name)
    image_temp = Image(temp_proc_path)
    image_temp.resize_image(230,230,1)
    image_temp.save_image(temp_proc_thumb_path)

    cloud_files_obj.upload_file(temp_proc_thumb_path, temp_proc_thumb_name)

    ifd.get_skin_mask_with_edge_detection()
    ifd.detect_image_features()

    rois = ifd.get_detected_rois()

    face = []
    breast = []
    breasts = []
    bikini_top = []
    midriff = []
    mons_pubis = []

    for r in rois:
        # print r
        #print rois[r]
        if r == 0 or r == 1 or r == 2:
            face.extend(rois[r])
        elif r == 3:
            breast.extend(rois[r])
        elif r == 4:
            breasts.extend(rois[r])
        elif r == 5:
            bikini_top.extend(rois[r])
        elif r == 6:
            midriff.extend(rois[r])
        elif r == 7:
            mons_pubis.extend(rois[r])

    # Cull image rois based on skin content

    if ifd.is_color():
        to_remove = []
        for i, roi in enumerate(breast):
            if ifd.get_skin_fraction(roi) < 0.3:
                to_remove.append(i)

        temp = []
        for i, roi in enumerate(breast):
            if i not in to_remove:
                temp.append(roi)
        breast = temp

        to_remove = []
        for i, roi in enumerate(breasts):
            if ifd.get_skin_fraction(roi) < 0.3:
                to_remove.append(i)
        temp = []
        for i, roi in enumerate(breasts):
            if i not in to_remove:
                temp.append(roi)
        breasts = temp

        to_remove = []
        for i, roi in enumerate(bikini_top):
            if ifd.get_skin_fraction(roi) < 0.1:
                to_remove.append(i)
        temp = []
        for i, roi in enumerate(bikini_top):
            if i not in to_remove:
                temp.append(roi)
        bikini_top = temp

        to_remove = []
        for i, roi in enumerate(midriff):
            if ifd.get_skin_fraction(roi) < 0.3:
                to_remove.append(i)
        temp = []
        for i, roi in enumerate(midriff):
            if i not in to_remove:
                temp.append(roi)
        midriff = temp

        to_remove = []
        for i, roi in enumerate(mons_pubis):
            if ifd.get_skin_fraction(roi) < 0.4:
                to_remove.append(i)
        temp = []
        for i, roi in enumerate(mons_pubis):
            if i not in to_remove:
                temp.append(roi)
        mons_pubis = temp

    #Convert ROIs into ImageROI objects

    face_objs = []
    breasts_objs = []
    bikini_top_objs = []
    midriff_objs = []
    mons_pubis_objs = []

    for roi in face:
        face_objs.append(ImageROI(roi))
    #haarcascade_breast output is not culled via overlap check
    for roi in breasts:
        breasts_objs.append(ImageROI(roi))
    for roi in bikini_top:
        bikini_top_objs.append(ImageROI(roi))
    for roi in midriff:
        midriff_objs.append(ImageROI(roi))
    for roi in mons_pubis:
        mons_pubis_objs.append(ImageROI(roi))

    #Cull ROIs based on overlap

    to_remove = []
    for i, roi_obj in enumerate(midriff_objs):
        for face_roi_obj in face_objs:
            if roi_obj.get_overlap_area(face_roi_obj):
                to_remove.append(i)
                break
    temp = []
    for i, roi_obj in enumerate(midriff_objs):
        if i not in to_remove:
            temp.append(roi_obj)
    midriff_objs = temp

    to_remove = []
    for i, roi_obj in enumerate(breasts_objs):
        popped_flag = 0

        for face_roi_obj in face_objs:
            if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                to_remove.append(i)
                popped_flag = 1
                break

        if popped_flag:
            continue

        for midriff_roi_obj in midriff_objs:
            if roi_obj.is_within_bounds(midriff_roi_obj.centroid()):
                to_remove.append(i)
                break
    temp = []
    for i, roi_obj in enumerate(breasts_objs):
        if i not in to_remove:
            temp.append(roi_obj)
    breasts_objs = temp

    to_remove = []
    for i, roi_obj in enumerate(bikini_top_objs):
        popped_flag = 0

        for face_roi_obj in face_objs:
            if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                to_remove.append(i)
                popped_flag = 1
                break

        if popped_flag:
            continue

        for midriff_roi_obj in midriff_objs:
            if roi_obj.is_within_bounds(midriff_roi_obj.centroid()):
                to_remove.append(i)
                break
    temp = []
    for i, roi_obj in enumerate(bikini_top_objs):
        if i not in to_remove:
            temp.append(roi_obj)
    bikini_top_objs = temp

    to_remove = []
    for i, roi_obj in enumerate(mons_pubis_objs):
        for face_roi_obj in face_objs:
            if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                to_remove.append(i)
                break
    temp = []
    for i, roi_obj in enumerate(mons_pubis_objs):
        if i not in to_remove:
            temp.append(roi_obj)
    mons_pubis_objs = temp


    #Select ROIs for blurring

    blur_rois = []

    for roi in breast:
        blur_rois.append(roi)

    for roi_obj in breasts_objs:
        blur_rois.append(roi_obj.get_roi_tuple())

    for roi_obj in bikini_top_objs:
        roi = roi_obj.get_roi_tuple()
        if ifd.get_skin_fraction(roi) > 0.5:
            blur_rois.append(roi)

    for roi_obj in mons_pubis_objs:
        blur_rois.append(roi_obj.get_roi_tuple())

    if len(blur_rois):
        #Blur the ROIs to be blurred
        ifd.image_gaussian_blur(blur_rois, 200)
        #and save the image with blurred ROIs
        temp_cens_path = os.path.join(temp_dir, temp_cens_name)
        ifd.save_image(temp_cens_path)
        cloud_files_obj.upload_file(temp_cens_path, temp_cens_name)

        temp_cens_thumb_path = os.path.join(temp_dir, temp_cens_thumb_name)
        image_temp = Image(temp_cens_path)
        image_temp.resize_image(230,230,1)
        image_temp.save_image(temp_cens_thumb_path)

        cloud_files_obj.upload_file(temp_cens_thumb_path, temp_cens_thumb_name)

        nosql_data['needs_moderation'] = 1
        nosql_data['approved'] = 0
        nosql_data['cens_image_cloud_path'] = temp_cens_name
        nosql_data['cens_image_thumb_cloud_path'] = temp_cens_thumb_name

        os.remove(temp_cens_path)
        os.remove(temp_cens_thumb_path)

    nosql_data['id'] = image_id
    nosql_data['image_cloud_path'] = temp_proc_name
    nosql_data['image_thumb_cloud_path'] = temp_proc_thumb_name
    nosql_data['ts'] = image_ts
    nosql_data['ts_'] = int(time.time())

    os.remove(temp_path)
    os.remove(temp_proc_path)
    os.remove(temp_proc_thumb_path)

    mongo_lock.acquire()
    mongo_collection.insert(nosql_data)
    results_data = {}
    results_data['id'] = job_id
    results_data['result'] = nosql_data
    results_data['ts_'] = int(time.time())
    mongo_collection2.insert(results_data)
    mongo_lock.release()

    lock.release()


th = ThreadPool(8)

i_g = 0


def gearman_listener(gearman_worker, gearman_job):
    data = json.loads(gearman_job.data)
    job_id = data['id']
    job_data = data['jobdata']

    print job_data

    global i_g
    image_id = job_data['image_id']
    image_ts = job_data['image_ts']
    src_container_name = job_data['cloud_container_name']
    dest_container_name = job_data['destination_cloud_container']
    uploader_id = job_data['uploader_id']
    uploaded_cloud_path = job_data['uploaded_cloud_path']
    # lock, ifd, cloud_files_obj, src_container_name, cloud_image_path, dest_container_name, job_id, image_id, image_ts
    th.push_work(thread_func,
                 [locks[i_g], feature_detectors[i_g], cloud_files_con[i_g], src_container_name, uploaded_cloud_path,
                  dest_container_name, job_id, image_id, image_ts])
    i_g = (i_g + 1) % len(locks)
    return "0"


gm_worker = gearman.GearmanWorker(['localhost:4730'])

#gm_worker.set_client_id('numero_uno')
gm_worker.register_task('ovrvue_imgproc', gearman_listener)

gm_worker.work()



