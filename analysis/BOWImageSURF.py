__author__ = 'Sushant'

import threading
import pickle
from os import listdir
from os.path import isfile, join, isdir

import numpy
import cv2

from ImageSURF import ImageSURF


FLANN_INDEX_KDTREE = 1


class BOWImageSURFDictionary(object):
    def __init__(self, path, num_words=100, num_cluster_iterations=10, resize_image=400, hessian_threshold=400,
                 notify_of_steps=False, multi_threading=1, max_num_threads=8):
        self.resize_image = resize_image
        self.num_words = num_words
        self.hessian_threshold = hessian_threshold
        self.notify_of_steps = notify_of_steps

        self.multi_threading = multi_threading
        self.max_num_threads = max_num_threads
        self.dictionary = None

        if self.multi_threading:
            self.lock = threading.Lock()
        else:
            self.lock = None

        self.train_map = {}
        fill_flag = 0
        for d in listdir(path):
            # print d
            p_d = join(path, d)
            if isdir(p_d):
                # print "is directory"
                self.train_map[d] = []
                for f in listdir(p_d):
                    #print f
                    self.train_map[d].append(join(p_d, f))
            elif isfile(p_d):
                if not fill_flag:
                    fill_flag = 1
                    self.train_map['.'] = []
                self.train_map['.'].append(p_d)

        if len(self.train_map):
            self.all_descriptors = numpy.empty([0, 128], numpy.float32)
            th = []
            for cl in self.train_map:
                for im in self.train_map[cl]:
                    if self.notify_of_steps:
                        print "Fetching descriptors for " + im
                    if self.multi_threading:
                        t = threading.Thread(target=self.fetch_descriptors, args=[im])
                        t.start()
                        th.append(t)

                        if len(th) > self.max_num_threads:
                            while len(th):
                                th.pop().join()
                    else:
                        self.fetch_descriptors(im)
            while len(th):
                th.pop().join()

            self.cluster(num_words, num_cluster_iterations)
        return

    def fetch_descriptors(self, im_file_path):
        im_surf = ImageSURF(im_file_path)
        im_surf.resize_image(self.resize_image, self.resize_image)
        _, des = im_surf.detect_and_compute_SURF(0, self.hessian_threshold)

        if self.multi_threading:
            self.lock.acquire()

        self.all_descriptors = numpy.vstack((self.all_descriptors, des))

        if self.multi_threading:
            self.lock.release()
        return

    def cluster(self, num_clusters, num_tries):
        if self.all_descriptors is not None:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv2.KMEANS_RANDOM_CENTERS
            compactness, labels, centers = cv2.kmeans(data=self.all_descriptors, K=num_clusters, bestLabels=None,
                                                      criteria=criteria,
                                                      attempts=num_tries, flags=flags)
            self.dictionary = centers
            return compactness, labels, centers
        return None

    def save(self, file_path):
        if self.dictionary is not None:
            numpy.save(file_path, self.dictionary)
        return


class BOWImageSURFClassifier(object):
    def __init__(self, load_files_path, train_images_path=None, hidden_layers_scheme=None, resize_image=400,
                 hessian_threshold=400):
        self.scheme = numpy.empty([0, 1], numpy.int)
        self.dictionary = None
        self.ann = cv2.ANN_MLP()
        self.words = None
        self.train_map = None
        self.binary_classes = None
        self.resize_image = resize_image
        self.hessian_threshold = hessian_threshold
        self.train_vectors = None
        self.train_labels = None
        self.train_files_count = 0
        self.train_mat_fill_index = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)

        if load_files_path is not None and isdir(load_files_path):
            trained_ann_file_name = join(load_files_path, "trained_ann.xml")
            dictionary_file_name = join(load_files_path, "dictionary.npy")
            class_map_file_name = join(load_files_path, "class_map.pkl")

            if not isfile(trained_ann_file_name):
                if isfile(dictionary_file_name):
                    self.dictionary = numpy.load(dictionary_file_name)

                    self.words = self.dictionary.shape[0]
                    print self.words
                    self.scheme = numpy.vstack((self.scheme, [self.words]))
                    if hidden_layers_scheme is None:
                        hidden_layers_scheme = numpy.zeros([2, 1], numpy.int)
                        hidden_layers_scheme[0][0] = 20
                        hidden_layers_scheme[1][0] = 20
                    self.scheme = numpy.vstack((self.scheme, hidden_layers_scheme))
                    self.scheme = numpy.vstack((self.scheme, [1]))

                    self.ann.create(self.scheme, cv2.ANN_MLP_SIGMOID_SYM)

                    if train_images_path is not None:
                        for d in listdir(train_images_path):
                            p_d = join(train_images_path, d)
                            if isdir(p_d):
                                # print "is directory"
                                if self.train_map is None:
                                    self.train_map = {}
                                self.train_map[d] = []
                                for f in listdir(p_d):
                                    # print f
                                    p_d_f = join(p_d, f)
                                    if isfile(p_d_f):
                                        self.train_map[d].append(p_d_f)
                                        self.train_files_count += 1

                    if self.train_map is not None:
                        self.train_vectors = numpy.zeros([self.train_files_count, self.words], numpy.float32)
                        self.train_labels = numpy.zeros([self.train_files_count, 1], numpy.float32)
                        for x in self.train_map:
                            if self.binary_classes is None:
                                self.binary_classes = {}
                                self.binary_classes[0] = "Not " + x
                                self.binary_classes[1] = x
                                with open(class_map_file_name, 'wb') as f:
                                    pickle.dump(self.binary_classes, f, pickle.HIGHEST_PROTOCOL)
                                for im in self.train_map[x]:
                                    self.extract_dictionary_features_for_training(im, 1)
                            else:
                                for im in self.train_map[x]:
                                    self.extract_dictionary_features_for_training(im, -1)
                        if len(self.train_vectors):
                            print "Training ANN...."
                            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001)
                            params = dict(term_crit=criteria, train_method=cv2.ANN_MLP_TRAIN_PARAMS_RPROP)
                            sample_weights = numpy.ones([self.train_files_count, 1], numpy.float32)
                            self.ann.train(inputs=self.train_vectors, outputs=self.train_labels,
                                           sampleWeights=sample_weights,
                                           flags=cv2.ANN_MLP_NO_INPUT_SCALE | cv2.ANN_MLP_NO_OUTPUT_SCALE,
                                           params=params)
                    self.ann.save(trained_ann_file_name)
            else:
                self.ann.load(trained_ann_file_name)
                if isfile(dictionary_file_name):
                    self.dictionary = numpy.load(dictionary_file_name)
                    self.words = self.dictionary.shape[0]

                if isfile(class_map_file_name):
                    with open(class_map_file_name, 'r') as f:
                        self.binary_classes = pickle.load(f)


    def extract_dictionary_features(self, im_file_path):
        if self.dictionary is not None:
            im_surf = ImageSURF(im_file_path)
            im_surf.resize_image(self.resize_image, self.resize_image)
            _, des = im_surf.detect_and_compute_SURF(0, self.hessian_threshold)
            matches = self.matcher.knnMatch(des, self.dictionary, k=2)
            good_matches = numpy.zeros([1, self.words], numpy.float32)
            for i, (m, n) in enumerate(matches):
                # print i
                # print m.queryIdx
                #print m.trainIdx
                #print n.queryIdx
                #print n.trainIdx
                #print "====="
                if m.distance < 0.7 * n.distance:
                    good_matches[0][m.trainIdx] += 1

            max_inst = 1
            for i in range(good_matches.shape[1]):
                if max_inst < good_matches[0][i]:
                    max_inst = good_matches[0][i]

            for i in range(good_matches.shape[1]):
                good_matches[0][i] = good_matches[0][i] / max_inst
            return good_matches
        return None

    def extract_dictionary_features_from_mat(self, im_mat):
        if self.dictionary is not None:
            im_surf = ImageSURF()
            im_surf.copy_mat(im_mat)
            im_surf.resize_image(self.resize_image, self.resize_image)
            _, des = im_surf.detect_and_compute_SURF(0, self.hessian_threshold)
            matches = self.matcher.knnMatch(des, self.dictionary, k=2)
            good_matches = numpy.zeros([1, self.words], numpy.float32)
            for i, (m, n) in enumerate(matches):
                # print i
                # print m.queryIdx
                #print m.trainIdx
                #print n.queryIdx
                #print n.trainIdx
                #print "====="
                if m.distance < 0.7 * n.distance:
                    good_matches[0][m.trainIdx] += 1

            max_inst = 1
            for i in range(good_matches.shape[1]):
                if max_inst < good_matches[0][i]:
                    max_inst = good_matches[0][i]

            for i in range(good_matches.shape[1]):
                good_matches[0][i] = good_matches[0][i] / max_inst
            return good_matches
        return None

    def extract_dictionary_features_for_training(self, im_file_path, label):
        if isfile(im_file_path):
            self.train_vectors[self.train_mat_fill_index] = self.extract_dictionary_features(im_file_path)
            self.train_labels[self.train_mat_fill_index] = label
            self.train_mat_fill_index += 1
        return

    def predict_label(self, im_file_path):
        if self.ann is not None and self.dictionary is not None and isfile(im_file_path):
            features = self.extract_dictionary_features(im_file_path)
            return self.ann.predict(features)
        return None

    def predict_label_for_mat(self, im_mat):
        if self.ann is not None and self.dictionary is not None :
            features = self.extract_dictionary_features_from_mat(im_mat)
            return self.ann.predict(features)
        return None

"""
import os

cwd = os.path.curdir

# Ib = BOWImageSURFDictionary(os.path.join(cwd, "..", "data", "curated_train"), 200, 30, 200, 10, True)
#dictionary_path = os.path.join(cwd, "..", "extra", "bow", "dictionary.npy")
#Ib.save(dictionary_path)
#print Ib.train_map

B = BOWImageSURFClassifier(os.path.join(cwd, "..", "extra", "bow"), os.path.join(cwd, "..", "data", "curated_train"),
                           None, 200, 10)
train_images_dir = os.path.join(cwd, "..", "data", "curated_train")
pos_dir = os.path.join(train_images_dir, "pos")
neg_dir = os.path.join(train_images_dir, "neg")
count = 0
pos = 0
neg = 0
for img in os.listdir(pos_dir):
    full_path = os.path.join(pos_dir, img)
    if os.path.isfile(full_path):
        label,p = B.predict_label(full_path)
        if p[0][0] < -0.06:
            pos += 1
        else:
            neg += 1
        count += 1

        if count % 50 == 0:
            print str(count) + "," +str(pos) + "," +str(neg)

print str(count) + "," +str(pos) + "," +str(neg)
count = 0
pos = 0
neg = 0

for img in os.listdir(neg_dir):
    full_path = os.path.join(neg_dir, img)
    if os.path.isfile(full_path):
        label,p = B.predict_label(full_path)
        if p[0][0] < -0.06:
            pos += 1
        else:
            neg += 1
        count += 1

        if count % 50 == 0:
            print str(count) + "," +str(pos) + "," +str(neg)

print str(count) + "," +str(pos) + "," +str(neg)
"""