import cv2

from read import *
from mask import *
from decode import *
       
img = cv2.imread('qr-code-2.png', cv2.IMREAD_GRAYSCALE)
height, width = img.shape # dimensions of the image

_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# Now binary_img is either 0 (black) or 255 (white)

finder_patterns_coords = findCoordonates(binary_img, height, width)

qr = positionedQR(getQR(binary_img, height, width), binary_img, height, width)

mask_id = get_mask_id(qr)

matrixWhereToApplyMask = computeMatrixOfUnmaskedCoordinates(qr)

qrDecoded = applyMask(matrixWhereToApplyMask, qr, mask_id)
print("QR decoded with mask ", mask_id)
for line in qrDecoded:
    print(line)

encoding_type = get_encoding_type(qrDecoded)
print(encoding_type)

message_len = get_message_len(qrDecoded, encoding_type)
print(message_len)

message = get_message(qrDecoded, encoding_type, message_len)
print(message)
