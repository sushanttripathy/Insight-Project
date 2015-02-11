__author__ = 'Sushant'
from skimage.feature import hog
from skimage import color, exposure
import cv2
import numpy

from Image import Image


class ImageHOG(Image):
    def __init__(self, file_name=None):
        self.HOG_descriptors = None
        self.HOG_image_mat = None
        super(ImageHOG, self).__init__(file_name)
        return

    def compute_HOG_descriptors(self, show_image=False, orientations=8, pixels_per_cell=(16, 16),
                                cells_per_block=(2, 2)):
        if self.image_mat is not None:
            image = color.rgb2gray(self.image_mat)
            if show_image:
                self.HOG_descriptors, self.HOG_image_mat = hog(image, orientations=orientations,
                                                               pixels_per_cell=pixels_per_cell,
                                                               cells_per_block=cells_per_block, visualise=True)
                self.HOG_image_mat = exposure.rescale_intensity(self.HOG_image_mat, in_range=(0, 0.02))
                cv2.imwrite("hog.png", self.HOG_image_mat)
                cv2.imshow("Test", self.HOG_image_mat)
                cv2.waitKey(0)
            else:
                self.HOG_descriptors = hog(image, orientations=orientations, pixels_per_cell=pixels_per_cell,
                                           cells_per_block=cells_per_block, visualise=False)

            if self.HOG_descriptors is not None and self.HOG_descriptors.shape[0]:
                self.HOG_descriptors = self.HOG_descriptors / numpy.linalg.norm(self.HOG_descriptors)
            return self.HOG_descriptors
        return None


"""
import os

cwd = os.curdir
image_path = os.path.join(cwd, "..", "data", "image_check", "test1.jpg")



I = ImageHOG(image_path)
#I.resize_image(48,48, True)
I.orient_with_PCA()
I.show_image()
I.compute_HOG_descriptors(show_image=True)
"""

