import cv2

img = cv2.imread('siteQR.png', cv2.IMREAD_GRAYSCALE)

# Dimensions
height, width = img.shape
print(height, width)

print(img[100, 100])  # intensity of pixel (row=100, col=100)

_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# Now binary_img is either 0 (black) or 255 (white)
