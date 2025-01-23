import cv2

img = cv2.imread('siteQR.png', cv2.IMREAD_GRAYSCALE)

# Dimensions
height, width = img.shape
print(height, width)

print(img[100, 100])  # intensity of pixel (row=100, col=100)