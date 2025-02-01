def findMask(qr):
    print("Hello from a function {}", len(qr), " ", len(qr[0]))
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

    print(" LengthBlack = ", lengthBlack)

    # jump over the white line
    lengthBlack = lengthBlack + 1

    primitiveMask = [1, 0, 1, 0, 1]
    codedMaskId = []
    decodedMaskId = []

    for columnIndex in range(0, 5):
        codedMaskId.append(qr[lengthBlack][columnIndex])

    print("codedMask = ", codedMaskId, lengthBlack, " ", columnIndex)
    for i in range(len(codedMaskId)):
        decodedMaskId.append(codedMaskId[i] ^ primitiveMask[i])
    print("decodedMask = ", decodedMaskId)

    # first two bits are for error correction, so we drop them
    decodedMaskId.pop(0)
    decodedMaskId.pop(0)
    print("after dropping the first two bits decodedMask = ", decodedMaskId)
    matrixMask = getMatrixMask(decodedMaskId)


def getMatrixMask(decodedMask):
    maxtrixMask = []
    if (decodedMask == [0, 0, 0]):
        maxtrixMask = [
            [1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1]
        ]
    elif (decodedMask == [0, 0, 1]):
        maxtrixMask = [
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0]
        ]
    elif (decodedMask == [0, 1, 0]):
        maxtrixMask = [
            [1, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 0]
        ]
    elif (decodedMask == [0, 1, 1]):
        maxtrixMask = [
            [1, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 1],
            [0, 1, 0, 0, 1, 0],
            [1, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 1],
            [0, 1, 0, 0, 1, 0]
        ]
    else:
        print("Error, the mask ", decodedMask, " is not supported!")
    #elif ( decodeMask == [] )

    # Todo: In the article there are 4 more known masks that can be used.
    # https://medium.com/@r00__/decoding-a-broken-qr-code-39fc3473a034

    return maxtrixMask
