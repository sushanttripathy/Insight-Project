__author__ = 'Sushant'
from ImageFeatureDetect import ImageFeatureDetect, ImageROI
import os

class AnalyseImage(object):
    def __init__(self, cascades_dir):
        self.image_feature_detector = ImageFeatureDetect()

        face_cascade_1 = os.path.join(cascades_dir, "face", "haarcascade_frontalface_alt_tree.xml")
        # face_cascade_2 = os.path.join(cascade_dir, "face", "haarcascade_profileface.xml")
        # face_cascade_2 = os.path.join(cascade_dir, "face", "lbpcascade_frontalface.xml")
        face_cascade_2 = os.path.join(cascades_dir, "face", "haarcascade_frontalface_alt.xml")
        face_cascade_3 = os.path.join(cascades_dir, "face", "hogcascade_face_24x24_d3_s17.xml")

        breast_cascade_1 = os.path.join(cascades_dir, "breast", "haarcascade_breast.xml")
        breast_cascade_2 = os.path.join(cascades_dir, "breast", "hogcascade_breasts_36x36-d3_1_17.xml")

        bikini_top_cascade = os.path.join(cascades_dir, "bikini_top", "haarcascade_bikinitop_24x24_d2_s21.xml")

        midriff_cascade = os.path.join(cascades_dir, "midriff", "hogcascade_midriff_36x36-d3_1_17.xml")

        mons_pubis_cascade = os.path.join(cascades_dir, "mons_pubis", "hogcascade_32x32_d3_s11.xml")

        self.image_feature_detector.load_cascade(face_cascade_1)
        self.image_feature_detector.load_cascade(face_cascade_2)
        self.image_feature_detector.load_cascade(face_cascade_3)

        self.image_feature_detector.load_cascade(breast_cascade_1)
        self.image_feature_detector.load_cascade(breast_cascade_2)

        self.image_feature_detector.load_cascade(bikini_top_cascade)

        self.image_feature_detector.load_cascade(midriff_cascade)

        self.image_feature_detector.load_cascade(mons_pubis_cascade)

    def analyse_image(self, image_path, image_out_path):
        self.image_feature_detector.load_image(image_path)
        self.image_feature_detector.resize_image(400, 400)
        self.image_feature_detector.get_skin_mask_with_edge_detection()
        self.image_feature_detector.detect_image_features()
        rois = self.image_feature_detector.get_detected_rois()

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

        if self.image_feature_detector.is_color():
            to_remove = []
            for i, roi in enumerate(breast):
                if self.image_feature_detector.get_skin_fraction(roi) < 0.3:
                    to_remove.append(i)

            temp = []
            for i, roi in enumerate(breast):
                if i not in to_remove:
                    temp.append(roi)
            breast = temp

            to_remove = []
            for i, roi in enumerate(breasts):
                if self.image_feature_detector.get_skin_fraction(roi) < 0.3:
                    to_remove.append(i)
            temp = []
            for i, roi in enumerate(breasts):
                if i not in to_remove:
                    temp.append(roi)
            breasts = temp

            to_remove = []
            for i, roi in enumerate(bikini_top):
                if self.image_feature_detector.get_skin_fraction(roi) < 0.1:
                    to_remove.append(i)
            temp = []
            for i, roi in enumerate(bikini_top):
                if i not in to_remove:
                    temp.append(roi)
            bikini_top = temp

            to_remove = []
            for i, roi in enumerate(midriff):
                if self.image_feature_detector.get_skin_fraction(roi) < 0.3:
                    to_remove.append(i)
            temp = []
            for i, roi in enumerate(midriff):
                if i not in to_remove:
                    temp.append(roi)
            midriff = temp

            to_remove = []
            for i, roi in enumerate(mons_pubis):
                if self.image_feature_detector.get_skin_fraction(roi) < 0.4:
                    to_remove.append(i)
            temp = []
            for i, roi in enumerate(mons_pubis):
                if i not in to_remove:
                    temp.append(roi)
            mons_pubis = temp

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

        super_explicit = False
        mid_explicit = True

        blur_rois = []

        for roi in breast:
            blur_rois.append(roi)
            super_explicit = True

        for roi_obj in breasts_objs:
            blur_rois.append(roi_obj.get_roi_tuple())
            super_explicit = True

        for roi_obj in bikini_top_objs:
            roi = roi_obj.get_roi_tuple()
            if self.image_feature_detector.get_skin_fraction(roi) > 0.5:
                blur_rois.append(roi)
                mid_explicit = True

        for roi_obj in mons_pubis_objs:
            blur_rois.append(roi_obj.get_roi_tuple())
            super_explicit = True

        print image_path
        if len(blur_rois):
            self.image_feature_detector.image_gaussian_blur(blur_rois, 200)
        self.image_feature_detector.save_image(image_out_path)



