__author__ = 'Sushant'

import threading
import random

import cv2
import numpy

from Image import Image


class ImageFeatureDetect(Image):
    def __init__(self, file_name=None, max_small_image_width=400, max_small_image_height=400, multi_threading=True):
        self.multi_threading = multi_threading

        if self.multi_threading:
            self.lock = threading.Lock()
        else:
            self.lock = None

        self.small_image = None
        self.max_small_image_width = max_small_image_width
        self.max_small_image_height = max_small_image_height
        self.mask = None
        self.loaded_cascades = []
        self.detected_rois = {}
        self.skin_mask = None
        super(ImageFeatureDetect, self).__init__(file_name)
        return

    def load_image(self, file_name):
        super(ImageFeatureDetect, self).load_image(file_name)

        if self.image_mat is not None:
            small_image_width = self.max_small_image_width
            small_image_height = self.max_small_image_height
            width = self.image_mat.shape[1]
            height = self.image_mat.shape[0]

            change_width = float(small_image_width) / float(width)
            change_height = float(small_image_height) / float(height)

            if change_width <= 1 and change_height <= 1:
                if change_width < change_height:
                    small_image_height = int(change_width * height)
                else:
                    small_image_width = int(change_height * width)
            else:
                if change_width < change_height:
                    small_image_width = int(change_height * width)
                else:
                    small_image_height = int(change_width * height)
            temp_small_image = cv2.resize(self.image_mat, (small_image_width, small_image_height))
            gray_small_image = cv2.cvtColor(temp_small_image, cv2.COLOR_BGR2GRAY)
            self.small_image = cv2.equalizeHist(gray_small_image)
            return

    def load_cascade(self, file_name):
        c = cv2.CascadeClassifier()
        if c.load(file_name):
            self.loaded_cascades.append(c)
        else:
            print "Error loading cascade : " + file_name
        return

    def add_loaded_cascade(self, loaded_cascade):
        if loaded_cascade is not None:
            self.loaded_cascades.append(loaded_cascade)
        return

    def detect_image_features(self, min_feature_width=40, min_feature_height=40):
        if self.small_image is not None and len(self.loaded_cascades):
            if self.multi_threading:
                th = []
                for cascade_ind, loaded_cascade in enumerate(self.loaded_cascades):
                    t = threading.Thread(target=self.detect_image_features_using_cascade,
                                         args=[min_feature_width, min_feature_height, loaded_cascade, cascade_ind])
                    t.start()
                    th.append(t)
                while len(th):
                    _t = th.pop()
                    _t.join()
            else:
                for cascade_ind, loaded_cascade in enumerate(self.loaded_cascades):
                    self.detect_image_features_using_cascade(min_feature_width, min_feature_height, loaded_cascade,
                                                             cascade_ind)
        return

    def detect_image_features_using_cascade(self, min_feature_width, min_feature_height, loaded_cascade, cascade_ind):
        if loaded_cascade is not None and cascade_ind is not None:
            rois = loaded_cascade.detectMultiScale(self.small_image, 1.1, 3,
                                                   0 | cv2.cv.CV_HAAR_SCALE_IMAGE | cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT,
                                                   (min_feature_width, min_feature_height))
            if self.multi_threading:
                self.lock.acquire()
                self.detected_rois[cascade_ind] = rois
                self.lock.release()
            else:
                self.detected_rois[cascade_ind] = rois
        return

    def show_image_with_rois(self, window_name=None):
        if self.image_mat is not None and len(self.detected_rois):
            scale_x = float(self.image_mat.shape[1]) / float(self.small_image.shape[1])
            scale_y = float(self.image_mat.shape[0]) / float(self.small_image.shape[0])
            temp_image = numpy.copy(self.image_mat)
            num_cascades = float(len(self.loaded_cascades))
            for d in self.detected_rois:
                if len(self.detected_rois[d]):
                    if d >= 0 and d < (num_cascades / 3):
                        color_scalar = (
                            int(((num_cascades / 3 - d) / (num_cascades / 3)) * 255),
                            int((d / (num_cascades / 3)) * 255), 0)
                    elif d >= (num_cascades / 3) and d < (2 * num_cascades / 3):
                        color_scalar = (0, int(((2 * num_cascades / 3 - d) / (num_cascades / 3)) * 255),
                                        int(((d - (num_cascades / 3)) / (num_cascades / 3))) * 255)
                    else:
                        color_scalar = (int(((d - (2 * num_cascades / 3)) / (num_cascades / 3)) * 255), 0,
                                        int(((num_cascades - d) / (num_cascades / 3)) * 255))
                    for r in self.detected_rois[d]:
                        x = int(scale_x * r[0])
                        y = int(scale_y * r[1])
                        width = int(scale_x * r[2])
                        height = int(scale_y * r[3])
                        cv2.rectangle(temp_image, (x, y), (x + width, y + height), color_scalar, 2)
                        # print (x, y, width, height)
            temp_image2 = self.image_mat
            self.image_mat = temp_image
            self.show_image(window_name)
            self.image_mat = temp_image2
        return

    def get_detected_rois(self):
        if self.small_image is not None and self.image_mat is not None:
            rois = {}
            scale_x = float(self.image_mat.shape[1]) / float(self.small_image.shape[1])
            scale_y = float(self.image_mat.shape[0]) / float(self.small_image.shape[0])
            if self.detected_rois is not None:
                for d in self.detected_rois:
                    rois[d] = []
                    if len(self.detected_rois[d]):
                        for r in self.detected_rois[d]:
                            x = int(scale_x * r[0])
                            y = int(scale_y * r[1])
                            width = int(scale_x * r[2])
                            height = int(scale_y * r[3])
                            rois[d].append((x, y, width, height))
            return rois
        return {}


    def get_skin_mask(self, show_mask=0, apply_to_image=0, window_name=None):
        if self.image_mat is not None:
            hsv_image = cv2.cvtColor(self.image_mat, cv2.COLOR_BGR2HSV)
            bw = cv2.inRange(hsv_image, numpy.array([0, 10, 0], numpy.uint8), numpy.array([20, 150, 255], numpy.uint8))

            if show_mask:
                if window_name is None:
                    random_number = random.randint(0, 100000)
                    window_name = "image_" + repr(random_number)
                cv2.imshow(window_name, bw)
                cv2.waitKey(0)

            if apply_to_image:
                masked_image = cv2.bitwise_and(self.image_mat, self.image_mat, mask=bw)
                self.image_mat = masked_image
            return bw
        return None

    def get_canny_edges(self, show_edges=0, window_name=None, low_threshold=30, high_threshold=90, kernel_size=5):
        if self.image_mat is not None:
            gray_img = cv2.cvtColor(self.image_mat, cv2.COLOR_BGR2GRAY)
            blurred_img = cv2.blur(gray_img, (kernel_size, kernel_size))
            canny_image = cv2.Canny(blurred_img, low_threshold, high_threshold, kernel_size)
            if show_edges:
                if window_name is None:
                    random_number = random.randint(0, 100000)
                    window_name = "image_" + repr(random_number)
                cv2.imshow(window_name, canny_image)
            return canny_image
        return None


    def get_skin_mask_with_edge_detection(self, show_mask=0, apply_to_image=0, window_name=None, low_threshold=30,
                                          high_threshold=90, kernel_size=5):
        if self.image_mat is not None:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            skin_mask = self.get_skin_mask(0, 0)
            skin_closing = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            # cv2.imshow("Test2", skin_closing)
            #cv2.waitKey(0)
            canny_edges = self.get_canny_edges(0, None, low_threshold, high_threshold, kernel_size)
            fill_mask = cv2.copyMakeBorder(canny_edges, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            closing = cv2.morphologyEx(fill_mask, cv2.MORPH_CLOSE, kernel)
            #cv2.imshow("Test3", closing)
            #cv2.waitKey(0)
            flood_fill_points = []
            contours, _ = cv2.findContours(skin_closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                rect = cv2.boundingRect(c)
                if rect[2] < kernel_size or rect[3] < kernel_size:  #or rect[2] < 5 or rect[3] < 5:
                    continue
                #print cv2.contourArea(c)
                #cv2.rectangle(self.image_mat, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (128,128,128), 2)
                moments = cv2.moments(c)
                #print moments
                if moments['m00']:
                    centroid = (int(moments['m10'] / moments['m00']), int(
                        moments['m01'] / moments['m00']))
                else:
                    centroid = (int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2))
                #cv2.circle(self.image_mat, centroid, 1, (128,0,0))
                flood_fill_points.append(centroid)
            final_mask = numpy.zeros(skin_closing.shape, skin_closing.dtype)
            while len(flood_fill_points):
                point = flood_fill_points.pop()
                cv2.floodFill(final_mask, closing, point, (255,), flags=4)
            if window_name is None:
                random_number = random.randint(0, 100000)
                window_name = "image_" + repr(random_number)
            #final_mask = cv2.inRange(closing, 126, 129)
            temp = cv2.inRange(skin_closing, 1, 255)
            final_mask = cv2.bitwise_or(final_mask, temp)
            final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)
            if show_mask:
                cv2.imshow(window_name, final_mask)
                cv2.waitKey(0)
            if apply_to_image:
                masked_image = cv2.bitwise_and(self.image_mat, self.image_mat, mask=final_mask)
                self.image_mat = masked_image
            self.skin_mask = final_mask
            return final_mask
        return None

    def get_skin_fraction(self, roi):
        if self.skin_mask is not None:
            x = roi[0]
            y = roi[1]
            w = roi[2]
            h = roi[3]

            roi_ext = self.skin_mask[y:y + h, x:x + w]
            # roi_from_image = self.image_mat[y:y+h, x:x+w]
            # cv2.imshow("ROI", roi_ext)
            #cv2.imshow("ROI_image", roi_from_image)
            #cv2.waitKey(0)
            skin_pixels = numpy.count_nonzero(roi_ext)
            total_pixels = w * h
            skin_fraction = float(skin_pixels) / float(total_pixels)
            return skin_fraction
        return 0


class ImageROI(object):
    def __init__(self, roi):
        self.x = roi[0]
        self.y = roi[1]
        self.w = roi[2]
        self.h = roi[3]

    def centroid(self):
        c = (int(float(self.x) + float(self.w) / 2), int(float(self.y) + float(self.h) / 2))
        return c

    def get_roi_tuple(self):
        r = (self.x, self.y, self.w, self.h)
        return r

    def get_area(self):
        area = self.w * self.h
        return area

    def get_overlap_area(self, img_roi):
        start_x = 0
        end_x = 0

        start_y = 0
        end_y = 0

        if img_roi.x >= self.x and img_roi.x <= (self.x + self.w):
            start_x = img_roi.x
        elif self.x >= img_roi.x and self.x <= (img_roi.x + img_roi.w):
            start_x = self.x

        if (img_roi.x + img_roi.w) >= self.x and (img_roi.x + img_roi.w) <= (self.x + self.w):
            end_x = (img_roi.x + img_roi.w)
        elif (self.x + self.w) >= img_roi.x and (self.x + self.w) <= (img_roi.x + img_roi.w):
            end_x = (self.x + self.w)

        overlap_x = end_x - start_x

        if img_roi.y >= self.y and img_roi.y <= (self.y + self.h):
            start_y = img_roi.y
        elif self.y >= img_roi.y and self.y <= (img_roi.y + img_roi.h):
            start_y = self.y

        if (img_roi.y + img_roi.h) >= self.y and (img_roi.y + img_roi.h) <= (self.y + self.h):
            end_y = (img_roi.y + img_roi.h)
        elif (self.y + self.h) >= img_roi.y and (self.y + self.h) <= (img_roi.y + img_roi.h):
            end_y = (self.y + self.h)

        overlap_y = end_y - start_y
        overlap_area = overlap_x * overlap_y

        return overlap_area

    def get_overlap_fraction(self, image_roi):
        overlap_area = self.get_overlap_area(image_roi)
        area = self.w * self.h
        return float(overlap_area) / float(area)

    def is_within_bounds(self, point):
        point_x = point[0]
        point_y = point[1]

        if point_x >= self.x and point_x <= (self.x + self.w) and point_y >= self.y and point_y <= (self.y + self.h):
            return 1
        return 0


# ##################
###Example of usage
###################

import os

cwd = os.path.curdir
im_path = os.path.join(cwd, "test_images", "test.jpg")
print "Processing " + im_path

ifd = ImageFeatureDetect(im_path, 400, 400, 1)
ifd.resize_image(400, 400)

ifd.get_skin_mask_with_edge_detection(1)

# ifd.rotate_image(90)


cwd = os.path.curdir

cascade_dir = os.path.join(cwd, "cascades")

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

#ifd.show_image_with_rois()

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
    ifd.image_gaussian_blur(blur_rois, 80)
ifd.show_image()

print "Faces :"
print face

print "Breasts :"
print breast
print breasts

print "Bikini Top : "
print bikini_top

print "Midriff :"
print midriff

print "Down Under :"
print mons_pubis
