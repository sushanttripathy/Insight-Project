import matplotlib.pyplot as plt

from skimage.feature import hog
from skimage import io, color, exposure, transform
import numpy as np
import os

cwd = os.curdir
image_path = os.path.join(cwd, "..", "..", "data", "image_check", "test10.jpg")
image = color.rgb2gray(io.imread(image_path))
image = transform.resize(image, (400, 400))

#image = transform.resize(image, (48, 48))

fd, hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16),
                    cells_per_block=(1, 1), visualise=True)

fd = hog(image, orientations=8, pixels_per_cell=(16, 16),
                    cells_per_block=(1, 1))

fd = fd/np.linalg.norm(fd)

print hog_image.shape
print image.shape
print fd.shape
print fd.max()
print fd.min()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

ax1.axis('off')
ax1.imshow(image, cmap=plt.cm.gray)
ax1.set_title('Input image')

# Rescale histogram for better display
hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 0.02))

ax2.axis('off')
ax2.imshow(hog_image_rescaled, cmap=plt.cm.gray)
ax2.set_title('Histogram of Oriented Gradients')
plt.show()

io.imsave("out.png", hog_image_rescaled)

print os.path.dirname(os.path.realpath(__file__))