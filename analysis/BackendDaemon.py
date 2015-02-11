__author__ = 'Sushant'
from Framework import Framework, DownloadFiles
from ImageFeatureDetect import ImageROI, ImageFeatureDetect, Image
import mimetypes
import tempfile
import os
import json
import gearman


class BackendDaemon(object):
    def __init__(self):
        self.visual_inappropriate_content_detected = False
        pass

    def analyse_url(self, url):
        mime =  mimetypes.guess_type(url)
        major_mime =  (mime[0].split("/"))[0]
        F = Framework()
        temp_path = tempfile.mkdtemp()
        if major_mime == "image":
            F.get_images([url], temp_path)
        else:
            code, contents = F.get_url_contents(url)
            if 200 <= code <= 400:
                #either hit the page or were redirected, either way got valid HTML
                F.get_images(contents['images_urls'], temp_path)
                #TODO: send text for analysis
        for file_name in os.listdir(temp_path):
            full_path = os.path.join(temp_path, file_name)
            if os.path.isfile(full_path):
                self.analyse_image(full_path)

    def analyse_image(self, image_path):
        cwd = os.path.curdir
        ifd = ImageFeatureDetect(image_path, 400, 400)
        #ifd.resize_image(400, 400)
        ifd.get_skin_mask_with_edge_detection()
        cascade_dir = os.path.join(cwd, "..", "extra", "cascades")

        face_cascade_1 = os.path.join(cascade_dir, "face", "haarcascade_frontalface_alt_tree.xml")
        face_cascade_2 = os.path.join(cascade_dir, "face", "haarcascade_profileface.xml")
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

        ifd.detect_image_features()

        rois = ifd.get_detected_rois()

        face = []
        breast = []
        breasts = []
        bikini_top = []
        midriff = []
        mons_pubis = []

        for r in rois:
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
            for i, roi in enumerate(breast):
                if ifd.get_skin_fraction(roi) < 0.3:
                    breast.pop(i)
            for i, roi in enumerate(breasts):
                if ifd.get_skin_fraction(roi) < 0.3:
                    breasts.pop(i)
            for i, roi in enumerate(bikini_top):
                if ifd.get_skin_fraction(roi) < 0.1:
                    bikini_top.pop(i)
            for i, roi in enumerate(midriff):
                if ifd.get_skin_fraction(roi) < 0.3:
                    midriff.pop(i)
            for i, roi in enumerate(mons_pubis):
                if ifd.get_skin_fraction(roi) < 0.4:
                    mons_pubis.pop(i)

        # Convert ROIs into ImageROI objects

        face_objs = []
        breasts_objs = []
        bikini_top_objs = []
        midriff_objs = []
        mons_pubis_objs = []

        for roi in face:
            face_objs.append(ImageROI(roi))
        # haarcascade_breast output is not culled via overlap check
        for roi in breasts:
            breasts_objs.append(ImageROI(roi))
        for roi in bikini_top:
            bikini_top_objs.append(ImageROI(roi))
        for roi in midriff:
            midriff_objs.append(ImageROI(roi))
        for roi in mons_pubis:
            mons_pubis_objs.append(ImageROI(roi))

        #Cull ROIs based on overlap

        for i, roi_obj in enumerate(midriff_objs):
            popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_area(face_roi_obj):
                    midriff_objs.pop(i)
                    popped_flag = 1
                    break

            if popped_flag:
                continue

        for i, roi_obj in enumerate(breasts_objs):
            popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                    breasts_objs.pop(i)
                    popped_flag = 1
                    break

            if popped_flag:
                continue

            for midriff_roi_obj in midriff_objs:
                if roi_obj.is_within_bounds(midriff_roi_obj.centroid()):
                    breasts_objs.pop(i)
                    popped_flag = 1
                    break

        for i, roi_obj in enumerate(bikini_top_objs):
            popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                    bikini_top_objs.pop(i)
                    popped_flag = 1
                    break

            if popped_flag:
                continue

            for midriff_roi_obj in midriff_objs:
                if roi_obj.is_within_bounds(midriff_roi_obj.centroid()):
                    bikini_top_objs.pop(i)
                    popped_flag = 1
                    break

        for i, roi_obj in enumerate(mons_pubis_objs):
            popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                    mons_pubis_objs.pop(i)
                    popped_flag = 1
                    break

            if popped_flag:
                continue

        ifd.show_image_with_rois()

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
            self.visual_inappropriate_content_detected = True
            #Blur the ROIs to be blurred
            ifd.image_gaussian_blur(blur_rois, 80)
            #TODO: Save to a special path!


def gearman_listener(gearman_worker, gearman_job):
    data = json.loads(gearman_job.data)
    job_id = data['id']
    job_data = data['jobdata']
    url = job_data['url']
    B = BackendDaemon()
    B.analyse_url(url)
    return B.visual_inappropriate_content_detected


gm_worker = gearman.GearmanWorker(['localhost:4730'])

gm_worker.set_client_id('deux')
gm_worker.register_task('backend', gearman_listener)

gm_worker.work()


#B = BackendDaemon()
#B.analyse_url("http://www.something.com/1.jpeg")