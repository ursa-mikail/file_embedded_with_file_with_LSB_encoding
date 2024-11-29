import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.metrics.pairwise import euclidean_distances

# Load images

image_target = Image.open(file_target)
image_with_embedded = Image.open(file_with_embedded)

# Convert images to numpy arrays
image_target_np = np.array(image_target)
image_with_embedded_np = np.array(image_with_embedded)

# Display images with titles
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

axes[0].imshow(image_target_np)
axes[0].set_title('Target Image')
axes[0].axis('off')

axes[1].imshow(image_with_embedded_np)
axes[1].set_title('Image with Embedded Data')
axes[1].axis('off')

plt.show()

# Reshape images to 2D arrays
image_target_flat = image_target_np.reshape(-1, image_target_np.shape[-1])
image_with_embedded_flat = image_with_embedded_np.reshape(-1, image_with_embedded_np.shape[-1])

# Calculate Euclidean distances
distances = euclidean_distances(image_target_flat, image_with_embedded_flat)
mean_distance = np.mean(distances)

print(f"Mean Euclidean Distance: {mean_distance}")

