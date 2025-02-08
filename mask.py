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


# def getMatrixMask(decodedMask):
#     maxtrixMask = []
#     if decodedMask == [0 ,0 ,0]:
#         maxtrixMask = [
#             [1, 0, 1, 0, 1, 0],
#             [0, 1, 0, 1, 0, 1],
#             [1, 0, 1, 0, 1, 0],
#             [0, 1, 0, 1, 0, 1],
#             [1, 0, 1, 0, 1, 0],
#             [0, 1, 0, 1, 0, 1]
#         ]
#     elif decodedMask == [0, 0, 1]:
#         maxtrixMask = [
#             [1, 1, 1, 1, 1, 1],
#             [0, 0, 0, 0, 0, 0],
#             [1, 1, 1, 1, 1, 1],
#             [0, 0, 0, 0, 0, 0],
#             [1, 1, 1, 1, 1, 1],
#             [0, 0, 0, 0, 0, 0]
#         ]
#     elif (decodedMask == [0, 1, 0]):
#         maxtrixMask = [
#             [1, 0, 0, 1, 0, 0],
#             [1, 0, 0, 1, 0, 0],
#             [1, 0, 0, 1, 0, 0],
#             [1, 0, 0, 1, 0, 0],
#             [1, 0, 0, 1, 0, 0],
#             [1, 0, 0, 1, 0, 0]
#         ]
#     elif (decodedMask == [0, 1, 1]):
#         maxtrixMask = [
#             [1, 0, 0, 1, 0, 0],
#             [0, 0, 1, 0, 0, 1],
#             [0, 1, 0, 0, 1, 0],
#             [1, 0, 0, 1, 0, 0],
#             [0, 0, 1, 0, 0, 1],
#             [0, 1, 0, 0, 1, 0]
#         ]
#         #print (" Am ajuns aici ")
#     else:
#         print ("Error, the mask ", decodedMask, " is not supported!")
#     # elif ( decodeMask == [] )
#     # Todo: In the article there are 4 more known masks that can be used.
#     # https://medium.com/@r00__/decoding-a-broken-qr-code-39fc3473a034

#     return maxtrixMask

def excludeTimingPatterns(matrixToFill):
    # 6th row and 6th columns
    for i in range (0, len(matrixToFill)):
        matrixToFill[6][i] = 0

    for i in range (0, len(matrixToFill)):
        matrixToFill[i][6] = 0

def excludeDarkModule(matrixToFill):
    version = get_qr_version(matrixToFill)
    # According to https://www.thonky.com/qr-code-tutorial/module-placement-matrix#step-2-add-the-separators
    # the dark module is located at ([(4 * V) + 9], 8).
    matrixToFill[(4 * version) + 9][8] = 0

def excludeFormatInformationArea(matrixToFill):
    qrVersion = get_qr_version(matrixToFill)
    height = len(matrixToFill)

    # top left
    for i in range(0, 9):
        matrixToFill[8][i] = 0
        matrixToFill[i][8] = 0

    # top right
    for i in range(1, 9):
        matrixToFill[8][height -i] = 0

    # bottom right
    for i in range(1, 9):
        matrixToFill[height -i][8] = 0

    # According to https://www.thonky.com/qr-code-tutorial/module-placement-matrix#step-2-add-the-separators
    # for versions greater than 6 additional data needs to be added/ skipped when using the mask.
    if qrVersion >= 7:
        # top right
        for i in range(0, 7):
            for j in range (1, 4):
                matrixToFill[i][height - 8 -j] = 0

        for i in range(1, 4):
            for j in range (0, 7):
                matrixToFill[height - 8 -i][j] = 0

def getCoordinatesCentersForAlignmentPatterns(matrixToFill):
    # Accordint to https://www.thonky.com/qr-code-tutorial/alignment-pattern-locations
    # the centers of alignment patterns are hardcoded for each 5x5 squares.
    # note 1: They do not overlap with FinderPatterns!
    qrVersion = get_qr_version(matrixToFill)
    height = len(matrixToFill)

    pointsAlignment = []
    if qrVersion == 1:
        return pointsAlignment
    elif qrVersion == 2:
        pointsAlignment= [6, 18]
        # centers are ( 6, 6 ), ( 6, 18 ), ( 18, 6 ), ( 18, 18 )
        # note 1!!
    elif qrVersion == 3:
        pointsAlignment = [6, 22]
    elif qrVersion == 4:
        pointsAlignment = [6, 26]
    elif qrVersion == 5:
        pointsAlignment = [6, 30]
    elif qrVersion == 6:
        pointsAlignment = [6, 34]
    elif qrVersion == 7:
        pointsAlignment = [6, 22, 38]
    elif qrVersion == 8:
        pointsAlignment = [6, 24, 42]
    elif qrVersion == 9:
        pointsAlignment = [6, 26, 46]
    elif qrVersion == 10:
        pointsAlignment = [6, 28, 50]
    elif qrVersion == 11:
        pointsAlignment = [6, 30, 54]
    elif qrVersion == 12:
        pointsAlignment = [6, 32, 58]
    elif qrVersion == 13:
        pointsAlignment = [6, 34, 62]
    elif qrVersion == 14:
        pointsAlignment = [6, 26, 46, 66]
    elif qrVersion == 15:
        pointsAlignment = [6, 26, 48, 70]
    elif qrVersion == 16:
        pointsAlignment = [6, 26, 50, 74]
    elif qrVersion == 17:
        pointsAlignment = [6, 30, 54, 78]
    elif qrVersion == 18:
        pointsAlignment = [6, 30, 56, 82]
    elif qrVersion == 19:
        pointsAlignment = [6, 30, 58, 86]
    elif qrVersion == 20:
        pointsAlignment = [6, 34, 62, 90]
    elif qrVersion == 21:
        pointsAlignment = [6, 28, 50, 72, 94]
    elif qrVersion == 22:
        pointsAlignment = [6,26, 50, 74, 98]
    elif qrVersion == 23:
        pointsAlignment = [6, 30, 54, 78, 102]
    elif qrVersion == 24:
        pointsAlignment = [6, 28, 54, 80, 106]
    elif qrVersion == 25:
        pointsAlignment = [6, 32, 58, 84, 110]
    elif qrVersion == 26:
        pointsAlignment = [6, 30, 58, 86, 114]
    elif qrVersion == 27:
        pointsAlignment = [6, 34, 62, 90, 118]
    elif qrVersion == 28:
        pointsAlignment = [6, 26, 50, 74, 98, 122]
    elif qrVersion == 29:
        pointsAlignment = [6, 30, 54, 78, 102, 126]
    elif qrVersion == 30:
        pointsAlignment = [6, 26, 52, 78, 104, 130]
    elif qrVersion == 31:
        pointsAlignment = [6, 30, 56, 82, 108, 134]
    elif qrVersion == 32:
        pointsAlignment = [6, 34, 60, 86, 112, 138]
    elif qrVersion == 33:
        pointsAlignment = [6, 30, 58, 86, 114, 142]
    elif qrVersion == 34:
        pointsAlignment = [6, 34, 62, 90, 118, 146]
    elif qrVersion == 35:
        pointsAlignment = [6, 30, 54, 78, 102, 126, 150]
    elif qrVersion == 36:
        pointsAlignment = [6, 24, 50, 76, 102, 128, 154]
    elif qrVersion == 37:
        pointsAlignment = [6, 28, 54, 80, 106, 132, 158]
    elif qrVersion == 38:
        pointsAlignment = [6, 32, 58, 84, 110, 136, 162]
    elif qrVersion == 39:
        pointsAlignment = [6, 26, 54, 82, 110, 138, 166]
    elif qrVersion == 40:
        pointsAlignment = [6, 30, 58, 86, 114, 142, 170]





    centers = []
    centersThatOverlapWithFinderPatterns = [ ( 6, 6 ), ( 6, height -7 ), ( height -7, 6 ) ]
    print ( " centersThatOverlapWithFinderPatterns ")
    print ( centersThatOverlapWithFinderPatterns)
    for i in range (0, len(pointsAlignment)):
        for j in range (0, len(pointsAlignment)):
            found = False
            for k in range(0, len(centersThatOverlapWithFinderPatterns) ):
                if pointsAlignment[i] == centersThatOverlapWithFinderPatterns[k][0] and pointsAlignment[j] == centersThatOverlapWithFinderPatterns[k][1]:
                    found = True
            if not found:
                centers.append((pointsAlignment[i], pointsAlignment[j]))

    # compute the coordinates that are excluded
    return centers


def excludeAlignmentPatterns(matrixToFill):
    centers = getCoordinatesCentersForAlignmentPatterns(matrixToFill)
    # print("Centers : ")
    # print(centers)

    for i in range (0 , len(centers)):
        center = centers[i]
        cornerLeft = (center[0 ] -2, center[1 ] -2)
        for j in range(0, 5):
            for k in range(0, 5):
                matrixToFill[cornerLeft[0 ] +j][cornerLeft[1 ] +k] = 0

def excludeFinderAndSeparatorsPatterns(matrixToFill):
    height = len(matrixToFill)
    width = len(matrixToFill[0])

    # Size of corner squares is 7 x 7, but wee need additionals lines for separators
    # so the size 8 x 8.
    # print (" height ", len(matrixToFill) )
    # print ("width ", len(matrixToFill[0]))

    for i in range(0, 8):
        for j in range(0, 8):
            matrixToFill[i][j] = 0

    # bottom right
    for i in range(0, 8):
        for j in range(height -8, height):
            matrixToFill[i][j] = 0

    # bottom left
    for i in range(height -8, height):
        for j in range(0, 8):
            matrixToFill[i][j] = 0

def computeMatrixOfUnmaskedCoordinates(qr):
    matrixWhereToApplyMask = []
    for i in range(0, len(qr)):
        matrixWhereToApplyMask.append([])
        for j in range(0, len(qr[0])):
            matrixWhereToApplyMask[i].append(1)

    excludeFinderAndSeparatorsPatterns(matrixWhereToApplyMask)
    excludeTimingPatterns(matrixWhereToApplyMask)
    excludeDarkModule(matrixWhereToApplyMask)
    excludeFormatInformationArea(matrixWhereToApplyMask)

    excludeAlignmentPatterns(matrixWhereToApplyMask)
    # print("Excluded coordinates for mask: \n")
    # for line in matrixWhereToApplyMask:
    #     print(line)

    return matrixWhereToApplyMask

def flipBitAccordingToMask(maskCode, rowIndex, columnIndex):
    flipBit = False
    if maskCode == [0, 0, 0]:
        flipBit =  ( rowIndex + columnIndex ) % 2 == 0
    if maskCode == [0, 0, 1]:
        flipBit = rowIndex % 2 == 0
    if maskCode == [0, 1, 0]:
        flipBit =  columnIndex % 3 == 0
    if maskCode == [0, 1, 1]:
        flipBit =  ( rowIndex + columnIndex ) % 3 == 0
    if maskCode == [1, 0, 0]:
        flipBit =  ( rowIndex /2 + columnIndex /3 ) % 2 == 0
    if maskCode == [1, 0, 1]:
        flipBit =  ( (( rowIndex * columnIndex ) % 2) + ( ( rowIndex * columnIndex ) % 3 ) ) == 0
    if maskCode == [1, 1, 0]:
        flipBit =  ( ( ( rowIndex + columnIndex ) % 3 ) + ( ( rowIndex * columnIndex ) % 2 ) ) == 0
    if maskCode == [1, 1, 1]:
        flipBit =  ( ( ( rowIndex + columnIndex ) % 3) + rowIndex + columnIndex ) % 2 == 0

    return flipBit

def applyMask(matrixWhereToApply, qr, mask):
    qrDecoded = qr
    for i in range(0, len(qr)):
        for j in range(0, len(qr[0])):
            if matrixWhereToApply[i][j] == 1 and flipBitAccordingToMask(mask, i, j):
                qrDecoded[i][j] = 0 if qr[i][j] == 1 else 1

    return qrDecoded

