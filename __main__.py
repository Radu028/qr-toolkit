import cv2

from read import *
from mask import *
from decode import *
       
img = cv2.imread('qr-code.png', cv2.IMREAD_GRAYSCALE)
height, width = img.shape # dimensions of the image

_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# Now binary_img is either 0 (black) or 255 (white)

finder_patterns_coords = find_coordonates(binary_img, height, width)

qr = positioned_qr(get_qr(binary_img, height, width), binary_img, height, width)

mask_id = get_mask_id(qr)

unmasked_qr = remove_mask(qr, mask_id)
# for line in unmasked_qr:
#     print(line)

encoding_type = get_encoding_type(unmasked_qr)
# print(encoding_type)

# message_len = get_message_len(unmasked_qr, encoding_type)
# print(message_len)

correction_level = get_correction_level(unmasked_qr)
# print(correction_level)

message = get_message(unmasked_qr, encoding_type, correction_level)
print(message)

# This is just testing, if you want to see the print uncomment prints in the function get_matrix_write.
# for i in range(21, 70, 4):
#     qr_test = [[0 for _ in range(i)] for _ in range(i) ]
#     get_matrix_write(qr_test)

# Example function call to apply the best mask for a given qr matrix.
# (mask, qrWithMask) = compute_QR_with_the_best_mask(qr)
# print("QR  with mask applied for writing ", mask)
# for line in qrWithMask:
#     print(line)