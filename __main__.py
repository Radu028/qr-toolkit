import cv2

from findMask import *
from reading import *

def detectPositioning():
    
    global binary_img, height, width
    eyes = [[0,0],[0,0]]
    
    for i in range(height): #Search for the upper left corner
        for j in range(width//2):
            if binary_img[i, j] == 0:
                eyes[0][0]=(i, j)
            if eyes[0][0]:
                break
            
    for i in range(height): #Search for the upper right corner
        for j in range(width//2):
            if binary_img[i, width-1-j] == 0:
                eyes[0][1]=(i, width-1-j)
            if eyes[0][1]:
                break
            
    for i in range(height-1, -1, -1): #Search for the lower left corner
        for j in range(width//2):
            if binary_img[i, j] == 0:
                eyes[1][0]=(i, j)
            if eyes[1][0]:
                break
            
    for i in range(height-1, -1, -1): #Search for the lower right corner
        for j in range(width//2):
            if binary_img[i, width-1-j] == 0:
                eyes[1][1]=(i, width-1-j)
            if eyes[1][1]:
                break
            
    if eyes[0][0][1]>eyes[1][0][1]:
        eyes[0][0]=0
    elif eyes[0][0][1]<eyes[1][0][1]:
        eyes[1][0]=0
        
    if eyes[0][1][1]>eyes[1][1][1]:
        eyes[1][1]=0
    elif eyes[0][1][1]<eyes[1][1][1]:
        eyes[0][1]=0
    
    #Now i have the corners of the qr code(4 if i have a black pixel in the non-eye corner or 3 otherwise)
    
    if eyes[0].count(0) or eyes[1].count(0):
        return eyes
            
    eyePixels=0;
    
    #If i have a black pixel in the non-eye corner i count the lenght of an eye in pixels and if it happens to find the non-eye corner i return the eyes corner i replace it and return the coordonates of the corners with eyes
    for j in range(width):
        e1=binary_img[eyes[0][0][0],eyes[0][0][1]+j]
        e2=binary_img[eyes[0][1][0],eyes[0][1][1]-j]
        e3=binary_img[eyes[1][0][0],eyes[1][0][1]+j]
        e4=binary_img[eyes[1][1][0],eyes[1][1][1]-j]
            
        if e1==e2==e3==e4==0:
            eyePixels+=1
        elif e1==e2==e3==e4==255:
            break
        else:
            if e1!=e2:
                if e1!=e3:
                    eyes[0][0]=0
                else:
                    eyes[0][1]=0
                return eyes
            else:
                if e1!=e3:
                    eyes[1][0]=0
                else:
                    eyes[1][1]=0
            return eyes
            
    #I search for a difference between the eyes
    for i in range(eyePixels):
        for j in range(eyePixels):
            e1=binary_img[eyes[0][0][0]+i,eyes[0][0][1]+j]
            e2=binary_img[eyes[0][1][0]+i,eyes[0][1][1]-j]
            e3=binary_img[eyes[1][0][0]-i,eyes[1][0][1]+j]
            e4=binary_img[eyes[1][1][0]-i,eyes[1][1][1]-j]
                
            if not e1==e2==e3==e4:
                if e1!=e2:
                    if e1!=e3:
                        eyes[0][0]=0 #Replace the value of the corner with 0 if non-eye
                    else:
                        eyes[0][1]=0#Replace the value of the corner with 0 if non-eye
                    return eyes
                else:
                    if e1!=e3:
                        eyes[1][0]=0#Replace the value of the corner with 0 if non-eye
                    else:
                        eyes[1][1]=0#Replace the value of the corner with 0 if non-eye
                    return eyes
                
def getModule():
    global binary_img, width
    
    eyes=detectPositioning()
    
    module_size=0
    
    if eyes[0][0]==0:
        #Get the module size from the upper right corner
        for j in range(eyes[0][1][1],-1,-1): #Add pixels until i find a white one
            if binary_img[eyes[0][1][0], j]==255:
                break
            else:
                module_size+=1
    else:
        #Get the module size from the upper left corner
        for j in range(eyes[0][0][1],width): #Add pixels until i find a white one
            if binary_img[eyes[0][0][0], j]==255:
                break
            else:
                module_size+=1
            
    module_size//=7 #We know that the finder pattern is 7 modules long
    
    return module_size

def findCoordonates():
    global binary_img, height, width
    
    module_size=getModule();
    
    finder_patterns_coordsi=set({})
    finder_patterns_coordsj=set({})
    for i in range(height):
        for j in range(width//2):
            if binary_img[i, j] == 0:
                finder_patterns_coordsi.add(i)
                finder_patterns_coordsj.add(j)
            if binary_img[i, width-1-j] == 0:
                finder_patterns_coordsi.add(i)
                finder_patterns_coordsj.add(width-j-(module_size*7))
            if finder_patterns_coordsi:
                break
    
    ok=1
    for i in range(height-1, -1, -1):
        for j in range(width//2):
            if binary_img[i, j] == 0:
                finder_patterns_coordsi.add(i+1-(module_size*7))
                finder_patterns_coordsj.add(j)
                ok=0
            if binary_img[i, width-1-j] == 0:
                finder_patterns_coordsi.add(i+1-(module_size*7))
                finder_patterns_coordsj.add(width-j-(module_size*7))
                ok=0
            if not ok:
                break
    
    return [(min(finder_patterns_coordsi),min(finder_patterns_coordsj)),(min(finder_patterns_coordsi),max(finder_patterns_coordsj)),(max(finder_patterns_coordsi),min(finder_patterns_coordsj))]

def getQR():
    eyes=detectPositioning()
    module_size=getModule()
    
    qr=[]
    
    if eyes[0][0]!=0 and eyes[1][0]!=0: #If the left corners are eyes, than I generate the QR between them
        for i in range(eyes[0][0][0], eyes[1][0][0]+1, module_size):
            row = []
            if eyes[0][1]!=0: #If the upper right corner is an eye, than I generate the QR between the upper corners
                for j in range(eyes[0][0][1], eyes[0][1][1]+1, module_size):
                    if binary_img[i, j] == 0:
                        row.append(1)
                    else:
                        row.append(0)
            else:#If the lower right corner is an eye, than I generate the QR between the right corners
                for j in range(eyes[1][0][1], eyes[1][1][1]+1, module_size):
                    if binary_img[i, j] == 0:
                        row.append(1)
                    else:
                        row.append(0)
                        
            qr.append(row)
    else:
        #If the right corners are eyes, than I generate the QR between them
        for i in range(eyes[0][1][0], eyes[1][1][0]+1, module_size):
            row = []
            
            if eyes[0][0]!=0: #If the upper left corner is an eye, than I generate the QR between the upper corners
                for j in range(eyes[0][0][1], eyes[0][1][1]+1, module_size):
                    if binary_img[i, j] == 0:
                        row.append(1)
                    else:
                        row.append(0)
            else:#If the lower left corner is an eye, than I generate the QR between the right corners
                for j in range(eyes[1][0][1], eyes[1][1][1]+1, module_size):
                    if binary_img[i, j] == 0:
                        row.append(1)
                    else:
                        row.append(0)
            
            qr.append(row)
    
    return qr

def rotation90clockwise(qr):
    n = len(qr)
    for i in range(n // 2):
        for j in range(i, n - i - 1):
            temp = qr[i][j]
            qr[i][j] = qr[n - 1 - j][i]
            qr[n - 1 - j][i] = qr[n - 1 - i][n - 1 - j]
            qr[n - 1 - i][n - 1 - j] = qr[j][n - 1 - i]
            qr[j][n - 1 - i] = temp
    return qr

def rotation90counterclockwise(qr):
    n = len(qr)
    for i in range(n // 2):
        for j in range(i, n - i - 1):
            temp = qr[i][j]
            qr[i][j] = qr[j][n - 1 - i]
            qr[j][n - 1 - i] = qr[n - 1 - i][n - 1 - j]
            qr[n - 1 - i][n - 1 - j] = qr[n - 1 - j][i]
            qr[n - 1 - j][i] = temp
    return qr

def rotation180(qr):
    n = len(qr)
    for i in range(n // 2):
        for j in range(n):
            qr[i][j], qr[n - 1 - i][n - 1 - j] = qr[n - 1 - i][n - 1 - j], qr[i][j]
    return qr

def positionedQR(qr): #Rotates the QR if needed
    
    eyes=detectPositioning()
    
    if eyes[0][0]==0:
        qr=rotation180(qr)
        
    if eyes[0][1]==0:
        qr=rotation90clockwise(qr)
        
    if eyes[1][0]==0:
        qr=rotation90counterclockwise(qr)
        
    return qr
       
img = cv2.imread('image2.jpeg', cv2.IMREAD_GRAYSCALE)

# Dimensions
height, width = img.shape

_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# Now binary_img is either 0 (black) or 255 (white)

finder_patterns_coords=findCoordonates()

qr = positionedQR(getQR())

decodedMaskId = findMask(qr)

qrVersion = computeQrVersion(qr)

matrixWhereToApplyMask = computeMatrixOfUnmaskedCoordinates(qr)

qrDecoded = applyMask(matrixWhereToApplyMask, qr, decodedMaskId)
print("QR decoded with mask ", decodedMaskId)
for line in qrDecoded:
    print(line)

encoding_type = get_encoding_type(qrDecoded)
print(encoding_type)

message_len = get_message_len(qrDecoded, encoding_type)
print(message_len)

message = get_message(qrDecoded, encoding_type, message_len)
print(message)
