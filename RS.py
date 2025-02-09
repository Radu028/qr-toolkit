import matplotlib.pyplot as plt
import reedsolo

def encode(message):

    encodedMessage = "0100"  # Byte mode indicator
    
    #Determine the length field size(8 bits versions 1-9/ 16 10-26/ 24 27-40)
    charCount = len(message)
    if charCount < 2**8: #8 bits
        charCountBits = format(charCount, '08b')
    elif charCount < 2**16: #16 bits
        charCountBits = format(charCount, '016b')
    else: #24 bits
        charCountBits = format(charCount, '024b')
    
    encodedMessage += charCountBits #Character count field
    
    #Encoded message
    for character in message:
        encodedMessage += format(ord(character), '08b')
    
    encodedMessage += '0000' #Terminator field
    
    #Ensure the length is a multiple of 8
    while len(encodedMessage) % 8 != 0:
        encodedMessage += '0'
    
    return encodedMessage

def encodeRS(encodedMessage):
    #Convert the binary string to a byte array
    byte_array = bytearray(int(encodedMessage[i:i+8], 2) for i in range(0, len(encodedMessage), 8))
    
    rs = reedsolo.RSCodec(7)  #7 symbols of error correction
    
    #Encode the message using Reed-Solomon encoding
    encodedMessageRS = rs.encode(byte_array)
    
    #Convert the encoded message to a binary string
    encodedMessageRS_str = ''.join(format(byte, '08b') for byte in encodedMessageRS)
    
    return encodedMessageRS_str

def makeMatrixBeforeMask():
    global message
    
    #Dimensions for the versions of QR(Byte,L)
    qrByteCapacity=[17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321, 367, 425, 458, 520, 586, 644, 718, 792, 858, 929, 1003, 1091, 1171, 1273, 1367, 1465, 1528, 1628, 1732, 1840, 1952, 2068, 2188, 2303, 2431, 2563, 2699, 2809, 2953]
    encodedMessage=encode(message)
    lenghtEncMess=len(encodedMessage)
    
    #Searches the version type
    version=None
    
    for i in range(len(qrByteCapacity)-1,-1,-1):
        if qrByteCapacity[i]>=lenghtEncMess:
            version=i+1
            
    if version: #If we have a version we continue
        matrixLenght=qrByteCapacity[i-1] 
        QRMatrix=[[0*matrixLenght] for i in range(matrixLenght)] #Create a matrix
        
        encodedMessageRS_str=encodeRS(encodedMessage) #version+lenght+message+end+reeds in binary
        print(encodedMessage, encodedMessageRS_str, sep='\n\n')
        
        # for i in range(0,len(QRMatrix),2):
        #     QRMatrix[6][i]=1
        #     QRMatrix[i][6]=1
        
        # for i in range(7):
        #     #First eye
        #     QRMatrix
        
        # plt.imshow(QRMatrix, cmap='gray_r')
        # plt.axis('off')
        # plt.show()
        
    else:
        print("The text is longer than the biggest version!")
        print("Reduce the characters of your text... =(")
        return

message=input("Message: ") #The input that will be made a QR code

makeMatrixBeforeMask()
