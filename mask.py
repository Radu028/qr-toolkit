from utils import *

def get_mask_id(qr):
    length_black = 0
    stop = 0
    for row_index in range(0, len(qr)):
        for column_index in range(0, len(qr[row_index])):
            if qr[row_index][column_index] != 1:
                stop = 1
                break
            length_black += 1
        if stop == 1:
            break

    # jump over the white line
    length_black = length_black + 1

    primitive_mask = [1, 0, 1, 0, 1]
    coded_mask_id = []
    decoded_mask_id = []

    for column_index in range(0, 5):
        coded_mask_id.append(qr[length_black][column_index])

    for i in range(len(coded_mask_id) ):
        decoded_mask_id.append( coded_mask_id[i] ^ primitive_mask[i] )

    # first two bits are for error correction, so we drop them
    decoded_mask_id.pop(0)
    decoded_mask_id.pop(0)

    return decoded_mask_id

def is_bit_flipped(mask_code, row_index, column_index):
    if mask_code == [0, 0, 0]:
        return (row_index + column_index) % 2 == 0
    elif mask_code == [0, 0, 1]:
        return row_index % 2 == 0
    elif mask_code == [0, 1, 0]:
        return column_index % 3 == 0
    elif mask_code == [0, 1, 1]:
        return (row_index + column_index) % 3 == 0
    elif mask_code == [1, 0, 0]:
        return (row_index // 2 + column_index // 3) % 2 == 0
    elif mask_code == [1, 0, 1]:
        return ((row_index * column_index) % 2 + (row_index * column_index) % 3) == 0
    elif mask_code == [1, 1, 0]:
        return (((row_index * column_index) % 2 + (row_index * column_index) % 3) % 2) == 0 == 0
    elif mask_code == [1, 1, 1]:
        return (((row_index + column_index) % 2 + (row_index * column_index) % 3) % 2) == 0

def remove_mask(qr, mask):
    reserved = get_reserved_matrix(qr)
    unmasked_qr = [row[:] for row in qr]
    for i in range(len(qr)):
        for j in range(len(qr[0])):
            if not reserved[i][j] and is_bit_flipped(mask, i, j):
                unmasked_qr[i][j] = 0 if qr[i][j] == 1 else 1
    return unmasked_qr

