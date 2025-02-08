from utils import *

def get_mask_id(qr):
    lengthBlack = 0
    stop = 0
    for rowIndex in range(0, len(qr)):
        for columnIndex in range(0, len(qr[rowIndex])):
            if qr[rowIndex][columnIndex] != 1:
                stop = 1
                break
            lengthBlack += 1
        if stop == 1:
            break

    # jump over the white line
    lengthBlack = lengthBlack + 1

    primitiveMask = [1, 0, 1, 0, 1]
    codedMaskId = []
    decodedMaskId = []

    for columnIndex in range(0, 5):
        codedMaskId.append(qr[lengthBlack][columnIndex])

    for i in range(len(codedMaskId) ):
        decodedMaskId.append( codedMaskId[i] ^ primitiveMask[i] )

    # first two bits are for error correction, so we drop them
    decodedMaskId.pop(0)
    decodedMaskId.pop(0)

    return decodedMaskId

def flipBitAccordingToMask(maskCode, rowIndex, columnIndex):
    if maskCode == [0, 0, 0]:
        return (rowIndex + columnIndex) % 2 == 0
    elif maskCode == [0, 0, 1]:
        return rowIndex % 2 == 0
    elif maskCode == [0, 1, 0]:
        return columnIndex % 3 == 0
    elif maskCode == [0, 1, 1]:
        return (rowIndex + columnIndex) % 3 == 0
    elif maskCode == [1, 0, 0]:
        return (rowIndex // 2 + columnIndex // 3) % 2 == 0
    elif maskCode == [1, 0, 1]:
        return ((rowIndex * columnIndex) % 2 + (rowIndex * columnIndex) % 3) == 0
    elif maskCode == [1, 1, 0]:
        return (((rowIndex * columnIndex) % 2 + (rowIndex * columnIndex) % 3) % 2) == 0 == 0
    elif maskCode == [1, 1, 1]:
        return (((rowIndex + columnIndex) % 2 + (rowIndex * columnIndex) % 3) % 2) == 0

def applyMask(qr, mask):
    reserved = get_reserved_matrix(qr)
    unmasked_qr = [row[:] for row in qr]
    for i in range(len(qr)):
        for j in range(len(qr[0])):
            if not reserved[i][j] and flipBitAccordingToMask(mask, i, j):
                unmasked_qr[i][j] = 0 if qr[i][j] == 1 else 1
    return unmasked_qr

