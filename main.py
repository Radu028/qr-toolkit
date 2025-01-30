import cv2

img = cv2.imread('siteQR.png', cv2.IMREAD_GRAYSCALE)

# Dimensions
height, width = img.shape
# print(height, width)

# print(img[100, 100])  # intensity of pixel (row=100, col=100)

_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# Now binary_img is either 0 (black) or 255 (white)

module_size = None

# Search for Finder Pattern
finder_patterns = {}
for i in range(height):
    for j in range(width):
        if binary_img[i, j] == 0 and binary_img[i, j + 1] == 0:
            for k in range(width - j):
                if binary_img[i, j + k + 1] == 255:
                    finder_patterns[1] = {}
                    finder_patterns[1]["start"] = (i, j)
                    module_size = (k + 1) // 7
                    break
            if module_size:
                break
    if module_size:
        break

print(module_size)
