__author__ = 'Sushant'

import threading

from Image import Image


class ImageComponents(Image):
    def __init__(self, file_name=None, max_small_image_width=400, max_small_image_height=400, cascades=None,
                 adaptiveSkinDetectionCascades=None):
        self.lock = threading.Lock()
        self.small_image = None
        self.max_small_image_width = max_small_image_width
        self.max_small_image_height = max_small_image_height
        self.cascades = {}
        self.adaptiveSkinDetectionCascades = []
        if cascades is not None:
            for cascadeName in cascades:
                self.cascades[cascadeName] = cascades[cascadeName]

        if adaptiveSkinDetectionCascades is not None:
            for cascade in adaptiveSkinDetectionCascades:
                self.adaptiveSkinDetectionCascades.append(cascade)

        super(ImageComponents, self).__init__(file_name)
        return

    def add_cascades(self, cascades):
        if cascades is not None:
            for cascadeName in cascades:
                self.cascades[cascadeName] = cascades[cascadeName]
        return

    def add_adaptive_skin_detection_cascades(self, adaptiveSkinDetectionCascades):
        if adaptiveSkinDetectionCascades is not None:
            for cascade in adaptiveSkinDetectionCascades:
                self.adaptiveSkinDetectionCascades.append(cascade)
        return

    def detect_skin_regions(self, detect_adaptive=1):
        result = {}

        return
