import cv2

img = cv2.imread('siteQR.png', cv2.IMREAD_GRAYSCALE)

# Dimensions
height, width = img.shape
# print(height, width)

# print(img[100, 100])  # intensity of pixel (row=100, col=100)

_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# Now binary_img is either 0 (black) or 255 (white)

module_size = None

# Search for Finder Pattern and get module size
finder_patterns = []
for i in range(height):
    for j in range(width):
        if binary_img[i, j] == 0 and binary_img[i, j + 1] == 0:
            for k in range(width - j):
                if binary_img[i, j + k + 1] == 255: # Assume that the first row of black pixels is the finder pattern
                    finder_patterns.append((i, j)) # Save only the starting point (top-left)
                    module_size = (k + 1) // 7
                    break
            if module_size:
                break
    if module_size:
        break

# Search for the second Finder Pattern
for i in range(finder_patterns[0][0], height):
    for j in range(finder_patterns[0][1] + 7 * module_size, width):
        # Check if the pixels from (i, j) to (i + 6 * module_size, j) and (i, j) to (i, j + 6 * module_size) are black
        for k in range(6 * module_size):
            if binary_img[i + k, j] == 255 or binary_img[i, j + k] == 255:
                break
        else:
            finder_patterns.append((i, j))
            break
    if len(finder_patterns) == 2:
        break

# Using the two Finder Patterns, we can now extract the third one without iterating through the whole image
finder_patterns.append((finder_patterns[1][1], finder_patterns[0][1])) # TODO: Test this later to see if it works for any QR Code
for line in finder_patterns:
    print(line)
