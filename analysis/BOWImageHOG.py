__author__ = 'Sushant'
import os
import pickle

from sklearn import cluster, neighbors, metrics, svm
import numpy
from sklearn.decomposition import PCA
import cv2

from ImageHOG import ImageHOG


class SVMImageHOG(object):
    def __init__(self, trained_files_dir, number_of_words=50, training_images_dir=None, resize_images=(48, 48)):
        self.base_trained_files_dir = trained_files_dir
        self.vectors_list = []
        self.words = None
        self.num_words = number_of_words
        self.resize_images = resize_images
        self.training_images_dir = training_images_dir
        self.neighbours = None
        self.svm = None
        self.mlp = None

    def aggregate_vectors(self, training_images_dir):
        for image_name in os.listdir(training_images_dir):
            if image_name != "." and image_name != "..":
                full_path = os.path.join(training_images_dir, image_name)
                # print full_path
                if os.path.isfile(full_path):
                    #print full_path
                    Im = ImageHOG(full_path)
                    #Im.show_image()
                    Im.orient_with_PCA()
                    #Im.show_image()
                    Im.resize_image(self.resize_images[0], self.resize_images[1], False)
                    vec = Im.compute_HOG_descriptors()
                    if vec is not None:
                        #print vec
                        self.vectors_list.append(vec)
                elif os.path.isdir(full_path):
                    self.aggregate_vectors(full_path)

    def build_dictionary(self):
        pca = PCA(n_components=self.num_words).fit(self.vectors_list)
        k_means = cluster.KMeans(init=pca.components_, n_clusters=self.num_words, n_init=1)
        k_means.fit(self.vectors_list)
        self.words = k_means.cluster_centers_.squeeze()
        print self.words.shape


    def save_dictionary(self, dictionary_path):
        numpy.save(dictionary_path, self.words)

    def load_dictionary(self, dictionary_path):
        self.words = numpy.load(dictionary_path)

    def get_labels_from_knn(self, image_path):
        if self.words is not None:
            if self.neighbours is None:
                self.neighbours = neighbors.NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(self.words)
            Im = ImageHOG(image_path)
            Im.orient_with_PCA()
            # Im.show_image()
            Im.resize_image(self.resize_images[0], self.resize_images[1], False)
            vec = Im.compute_HOG_descriptors()
            distances, indices = self.neighbours.kneighbors(vec)
            return distances, indices

    def get_distances(self, image_path):
        if self.words is not None:
            Im = ImageHOG(image_path)
            Im.orient_with_PCA()
            # Im.show_image()
            Im.resize_image(self.resize_images[0], self.resize_images[1], False)
            vec = Im.compute_HOG_descriptors()
            distances = metrics.pairwise.pairwise_distances(vec, self.words)
            #distances = distances/numpy.linalg.norm(distances)
            return distances

    def train_svm(self):
        train_vecs = []
        train_labels = []

        pos_dir = os.path.join(self.training_images_dir, "pos")

        for file_name in os.listdir(pos_dir):
            full_path = os.path.join(pos_dir, file_name)
            distances = self.get_distances(full_path)
            if distances is not None:
                train_vecs.append(distances[0])
                train_labels.append(1)

        neg_dir = os.path.join(self.training_images_dir, "neg")
        for file_name in os.listdir(neg_dir):
            full_path = os.path.join(neg_dir, file_name)
            distances = self.get_distances(full_path)
            if distances is not None:
                train_vecs.append(distances[0])
                train_labels.append(0)

        self.svm = svm.SVC()
        self.svm.fit(train_vecs, train_labels)

    def save_svm(self, svm_file_path):
        with open(svm_file_path, "wb") as out_file:
            pickle.dump(self.svm, out_file, pickle.HIGHEST_PROTOCOL)

    def load_svm(self, svm_file_path):
        with open(svm_file_path, "rb") as in_file:
            self.svm = pickle.load(in_file)

    def predict_with_svm(self, image_path):
        if self.svm is not None and self.words is not None:
            distances = self.get_distances(image_path)
            if distances is not None:
                res = self.svm.predict(distances[0])
                return res[0]

    def train_mlp(self):
        train_vecs = []
        train_labels = []

        pos_dir = os.path.join(self.training_images_dir, "pos")

        for file_name in os.listdir(pos_dir):
            full_path = os.path.join(pos_dir, file_name)
            distances = self.get_distances(full_path)
            if distances is not None:
                train_vecs.append(distances[0])
                train_labels.append(1)

        neg_dir = os.path.join(self.training_images_dir, "neg")
        for file_name in os.listdir(neg_dir):
            full_path = os.path.join(neg_dir, file_name)
            distances = self.get_distances(full_path)
            if distances is not None:
                train_vecs.append(distances[0])
                train_labels.append(-1)

        self.mlp = cv2.ANN_MLP()
        scheme = numpy.empty([0, 1], numpy.int)
        scheme = numpy.vstack((scheme, [self.num_words]))
        hidden_layers_scheme = numpy.zeros([2, 1], numpy.int)
        hidden_layers_scheme[0][0] = 20
        hidden_layers_scheme[1][0] = 20
        scheme = numpy.vstack((scheme, hidden_layers_scheme))
        scheme = numpy.vstack((scheme, [1]))
        print scheme
        self.mlp.create(scheme, cv2.ANN_MLP_SIGMOID_SYM)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001)
        params = dict(term_crit=criteria, train_method=cv2.ANN_MLP_TRAIN_PARAMS_RPROP)
        sample_weights = numpy.ones([len(train_labels), 1], numpy.float32)
        self.mlp.train(inputs=numpy.array(train_vecs, dtype=numpy.float32),
                       outputs=numpy.array(train_labels, dtype=numpy.float32),
                       sampleWeights=sample_weights,
                       flags=cv2.ANN_MLP_NO_INPUT_SCALE | cv2.ANN_MLP_NO_OUTPUT_SCALE,
                       params=params)

    def predict_with_mlp(self, image_path):
        if self.mlp is not None and self.words is not None:
            distances = self.get_distances(image_path)
            input_matrix  = numpy.array(distances, dtype=numpy.float32)
            #print input_matrix
            if distances is not None:
                label, p = self.mlp.predict(input_matrix)
                #print label, p
                return p[0][0]


cwd = os.path.curdir
train_images_dir = os.path.join(cwd, "..", "data", "curated_train")
pos_dir = os.path.join(train_images_dir, "pos")
neg_dir = os.path.join(train_images_dir, "neg")

train_files_dir = os.path.join(cwd, "..", "extra", "bowtest")

B = SVMImageHOG(train_files_dir, 20, train_images_dir)
B.aggregate_vectors(pos_dir)
B.build_dictionary()
B.save_dictionary(os.path.join(train_files_dir, "dictionary.npy"))

# B.train_svm()
#B.save_svm(os.path.join(train_files_dir, "svm.pkl"))

B.train_mlp()

count = 0
pos = 0
neg = 0

for img in os.listdir(pos_dir):
    full_path = os.path.join(pos_dir, img)
    if os.path.isfile(full_path):
        p = B.predict_with_mlp(full_path)
        #print p
        if p >= 0:
            pos += 1
        else:
            neg += 1
        count += 1

        if count % 50 == 0:
            print str(count) + "," + str(pos) + "," + str(neg)

print str(count) + "," + str(pos) + "," + str(neg)
count = 0
pos = 0
neg = 0

for img in os.listdir(neg_dir):
    full_path = os.path.join(neg_dir, img)
    if os.path.isfile(full_path):
        p = B.predict_with_mlp(full_path)
        if p >= 0:
            pos += 1
        else:
            neg += 1
        count += 1

        if count % 50 == 0:
            print str(count) + "," + str(pos) + "," + str(neg)

print str(count) + "," + str(pos) + "," + str(neg)

#print B.predict(os.path.join(pos_dir, "1_0.jpg"))
#print B.predict(os.path.join(neg_dir, "0.png"))
"""
for img in os.listdir(os.path.join(train_images_dir, "pos")):
    if img != "." and img != "..":
        full_path = os.path.join(os.path.join(train_images_dir, "pos"), img)
        #B.get_labels(full_path)
        d =  B.get_distances(full_path)
        print d[0]
        print "==============="
"""