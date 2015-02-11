__author__ = 'Sushant'

import cv2

from Image import Image


class ImageSURF(Image):
    def __init__(self, file_name=None):
        self.SURF_keypoints = None
        self.SURF_descriptos = None
        super(ImageSURF, self).__init__(file_name)
        return

    def detect_and_compute_SURF(self, show_features=0, hessian_threshold=400):
        im_gray = cv2.cvtColor(self.image_mat, cv2.COLOR_BGR2GRAY)
        surf = cv2.SURF(hessian_threshold)
        self.SURF_keypoints, self.SURF_descriptors = surf.detectAndCompute(im_gray, None)

        if show_features:
            img2 = cv2.drawKeypoints(im_gray, self.SURF_keypoints, None, (255, 0, 0), 4)
            cv2.imshow("Test", img2)
            cv2.waitKey(0)
        return self.SURF_keypoints, self.SURF_descriptors

"""
import os

cwd = os.path.curdir
im_path = os.path.join(cwd, "..", "data", "image_check", "test10.jpg")
im = ImageSURF(im_path)
im.resize_image(400, 400)
kp, des = im.detect_and_compute_SURF(1, 5000)
print des.shape
"""

