__author__ = 'Sushant'

import random
from collections import namedtuple

import cv2
import numpy


Rect = namedtuple("Rect", "x y width height")


class Image(object):
    def __init__(self, file_name=None):
        self.image_mat = None
        self.file_name = None
        self.current_window_name = None
        self.load_image(file_name)
        return

    def load_image(self, file_name):
        if type(file_name) is not None:
            self.file_name = file_name
            self.image_mat = cv2.imread(file_name)
        return

    def resize_image(self, width=-1, height=-1, maintain_aspect_ratio=1):
        if self.image_mat is not None:
            old_width = self.image_mat.shape[1]
            old_height = self.image_mat.shape[0]

            new_width = width
            new_height = height

            if new_width == -1:
                new_width = old_width
            if new_height == -1:
                new_height = old_height

            if maintain_aspect_ratio:
                change_width = float(new_width) / float(old_width)
                change_height = float(new_height) / float(old_height)

                if change_width <= 1 and change_height <= 1:
                    if change_width > change_height:
                        # more change occurs in height
                        new_width = int(old_width * change_height)
                    elif change_width < change_height:
                        new_height = int(old_height * change_width)
                else:
                    if change_width > change_height:
                        # more change occurs in width
                        new_height = int(old_height * change_width)
                    elif change_width < change_height:
                        new_width = int(old_width * change_height)

            temp_mat = cv2.resize(self.image_mat, (new_width, new_height))
            self.image_mat = temp_mat
        return

    def show_image(self, window_name=None):

        if window_name is None:
            random_number = random.randint(0, 100000)
            window_name = "image_" + repr(random_number)

        if type(window_name) is not None and self.image_mat is not None:
            self.current_window_name = window_name
            cv2.namedWindow(window_name)
            cv2.imshow(window_name, self.image_mat)
            cv2.waitKey(0)
        return

    def save_image(self, file_name):
        if self.image_mat is not None:
            cv2.imwrite(file_name, self.image_mat)
        return

    def image_gaussian_blur(self, locations, blur_block_size=5):
        if self.image_mat is not None and type(locations) is list and len(locations):
            temp_mat = cv2.blur(self.image_mat, (blur_block_size, blur_block_size))
            for n in locations:
                # print n
                roi_to_blur = self.image_mat[n[1]:n[1] + n[3], n[0]:n[0] + n[2]]
                blurred_roi = temp_mat[n[1]:n[1] + n[3], n[0]:n[0] + n[2]]
                numpy.copyto(roi_to_blur, blurred_roi)
        return

    def rotate_image(self, rotation, x=None, y=None, scale=1):
        if self.image_mat is not None:
            rows = self.image_mat.shape[0]
            cols = self.image_mat.shape[1]
            if x is None:
                x = cols / 2
            if y is None:
                y = rows / 2
            M = cv2.getRotationMatrix2D((x, y), rotation, scale)
            # if rotation % 180 == 90 or rotation % 180 == -90:
            #    temp = cols
            #    cols = rows
            #    rows = temp
            dst = cv2.warpAffine(self.image_mat, M, (cols, rows))
            self.image_mat = dst
        return

    def equalize_intensity(self):
        if self.image_mat is not None:
            img = cv2.cvtColor(self.image_mat, cv2.COLOR_BGR2YCR_CB)
            split_img = cv2.split(img)
            equalized_hist = cv2.equalizeHist(split_img[0])
            split_img[0] = equalized_hist
            img = cv2.merge(split_img)
            img_ret = cv2.cvtColor(img, cv2.COLOR_YCR_CB2BGR)
            self.image_mat = img_ret
        return

    def cluster_colors(self, num_colors=16, num_attempts=3, apply_to_image=0):
        if self.image_mat is not None:
            lin = numpy.empty([self.image_mat.shape[0] * self.image_mat.shape[1], 3],
                              numpy.float32)  # self.image_mat.dtype)
            for y in range(0, self.image_mat.shape[0]):
                for x in range(0, self.image_mat.shape[1]):
                    color = [float(self.image_mat[y][x][0]), float(self.image_mat[y][x][1]),
                             float(self.image_mat[y][x][2])]
                    lin[y * self.image_mat.shape[1] + x] = color
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv2.KMEANS_RANDOM_CENTERS
            # print lin
            compactness, labels, centers = cv2.kmeans(data=lin, K=num_colors, bestLabels=None, criteria=criteria,
                                                      attempts=num_attempts, flags=flags)
            if apply_to_image:
                for y in range(0, self.image_mat.shape[0]):
                    for x in range(0, self.image_mat.shape[1]):
                        color_label = labels[y * self.image_mat.shape[1] + x]
                        color = centers[color_label]
                        self.image_mat[y][x] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
            return labels, centers
        return []

    def is_color(self):
        if self.image_mat is not None:
            channels = cv2.split(self.image_mat)

            means_0 = numpy.mean(channels[0])
            means_1 = numpy.mean(channels[1])
            means_2 = numpy.mean(channels[2])

            if means_0 != means_1 or means_1 != means_2:
                return 1

            std_0 = numpy.std(channels[0])
            std_1 = numpy.std(channels[1])
            std_2 = numpy.std(channels[2])

            if std_0 != std_1 or std_1 != std_2:
                return 1
        return 0

