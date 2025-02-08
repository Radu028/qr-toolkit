
import reedsolo
from utils import *

def get_encoding_type(qr):
    rows = len(qr)
    cols = len(qr[0])
    
    bytes = str(qr[rows - 1][cols - 1]) + str(qr[rows - 1][cols - 2]) + str(qr[rows - 2][cols - 1]) + str(qr[rows - 2][cols - 2])

    if bytes == "0001":
        return "Numeric"
    elif bytes == "0010":
        return "Alphanumeric"
    elif bytes == "0100":
        return "Byte"
    elif bytes == "1000":
        return "Kanji"
    
    return "Unknown"

def get_correction_level(qr):
    bytes = str(qr[0][8]) + str(qr[1][8])

    if bytes == "01":
        return "L"
    elif bytes == "00":
        return "M"
    elif bytes == "10":
        return "Q"
    elif bytes == "11":
        return "H"
    
    return "Unknown"
    
def get_message_len(qr, encoding_type):
    qr_version = get_qr_version(qr)
    
    if 1 <= qr_version <= 9:
        if encoding_type == "Numeric":
            info_len = 10
        elif encoding_type == "Alphanumeric":
            info_len = 9
        elif encoding_type == "Byte":
            info_len = 8
    elif 10 <= qr_version <= 26:
        if encoding_type == "Numeric":
            info_len = 12
        elif encoding_type == "Alphanumeric":
            info_len = 11
        elif encoding_type == "Byte":
            info_len = 16
    elif 27 <= qr_version <= 40:
        if encoding_type == "Numeric":
            info_len = 14
        elif encoding_type == "Alphanumeric":
            info_len = 13
        elif encoding_type == "Byte":
            info_len = 16

    start_row = len(qr) - 1 - 2

    message_len_bytes = ""
    for i in range(info_len):
        col = len(qr[0]) - 1 - (i % 2)
        row = start_row - (i // 2)
        message_len_bytes += str(qr[row][col])

    return int(message_len_bytes, 2)

def extract_bits(qr):
    n = len(qr)
    reserved = get_reserved_matrix(qr)

    # === Extract bits from the data area, following the standard reading path ===

    # The data reading path starts from the bottom-right corner and traverses
    # the matrix in vertical bands of 2 columns, alternating the direction of
    # traversal (up -> down / down -> up). It also skips column 6 (timing zone)
    # and reserved modules.
    result_bits = []
    col = n - 1
    # Direction indicator: up==True means traversal from the bottom row to the top,
    # otherwise from top to bottom.
    up = True

    while col > 0:
        # Skip column 6 (if encountered)
        if col == 6:
            col -= 1
        # For each pair of columns, the two columns (col and col-1) are traversed in vertical order.
        if up:
            r_range = range(n - 1, -1, -1)
        else:
            r_range = range(0, n)
        for r in r_range:
            for c in (col, col - 1):
                # If the module is not part of the function zone, the bit is added.
                if not reserved[r][c]:
                    result_bits.append(str(qr[r][c]))
        # Move to the next pair of columns and reverse the direction
        col -= 2
        up = not up

    return "".join(result_bits)

def get_ecc_codewords_count(version, ecc_level):
    lookup = {
        1: {'L': 7,  'M': 10, 'Q': 13, 'H': 17},
        2: {'L': 10, 'M': 16, 'Q': 22, 'H': 28},
        3: {'L': 15, 'M': 26, 'Q': 36, 'H': 44},
        4: {'L': 20, 'M': 36, 'Q': 52, 'H': 68},
    }
    return lookup[version][ecc_level]

def correct_bitstream(bitstream, version, ecc_level):
    # Check if the length of the bitstream is a multiple of 8;
    # if not, add pad bits (0s) until it reaches a multiple of 8.
    if len(bitstream) % 8 != 0:
        pad_length = 8 - (len(bitstream) % 8)
        print(f"Add {pad_length} bits (0) as padding.")
        bitstream += "0" * pad_length

    # Convert the bitstream into codewords (groups of 8 bits)
    codewords = [int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8)]
    nsym = get_ecc_codewords_count(version, ecc_level)
    try:
        rsc = reedsolo.RSCodec(nsym)
        corrected = rsc.decode(bytearray(codewords))
        # Transform the result (bytearray) into a bit string
        corrected_bitstream = "".join(f"{byte:08b}" for byte in corrected)
        return corrected_bitstream
    except reedsolo.ReedSolomonError as e:
        print("Eroare la corectarea Reed–Solomon:", e)
        return None



def get_message(qr, encoding_type, ecc_level="L"):
    # bits_list = extract_bits(qr)
    raw_bitstream = extract_bits(qr)
    # Convert the list of bits (0 and 1) into a string of '0'/'1' characters
    # bit_str = "".join(str(b) for b in bits_list)

    # After the specification, the first 4 bits are the mode indicator,
    # and the next bits are the length indicator (their number depends on the mode):
    n = len(qr)
    version = ((n - 21) // 4) + 1 if n >= 21 else 1
    print("Versiunea QR: ", version)

    if ecc_level != "L":
        corrected_bitstream = correct_bitstream(raw_bitstream, version, ecc_level)
        if corrected_bitstream is None:
            raise ValueError("Correction failed.")
        bit_str = corrected_bitstream
    else:
        bit_str = raw_bitstream
    
    if 1 <= version <= 9:
        if encoding_type == "Numeric":
            count_indicator_length = 10
        elif encoding_type == "Alphanumeric":
            count_indicator_length = 9
        elif encoding_type == "Byte":
            count_indicator_length = 8
    elif 10 <= version <= 26:
        if encoding_type == "Numeric":
            count_indicator_length = 12
        elif encoding_type == "Alphanumeric":
            count_indicator_length = 11
        elif encoding_type == "Byte":
            count_indicator_length = 16
    elif 27 <= version <= 40:
        if encoding_type == "Numeric":
            count_indicator_length = 14
        elif encoding_type == "Alphanumeric":
            count_indicator_length = 13
        elif encoding_type == "Byte":
            count_indicator_length = 16
    else:
        raise ValueError("Versiunea QR necunoscută: " + str(version))
    
    # Calc message len
    message_len = int(bit_str[4:4 + count_indicator_length], 2)
    print("Lungimea mesajului: ", message_len)
    
    # Skip the first 4 bits (mode indicator) and the length indicator
    pos = 4 + count_indicator_length

    message = ""
    
    if encoding_type == "Byte":
        # Every character is encoded on 8 bits
        for _ in range(message_len):
            byte_bits = bit_str[pos:pos + 8]
            pos += 8
            # Convert the bits to a number and then to a character
            message += chr(int(byte_bits, 2))
    
    elif encoding_type == "Alphanumeric":
        table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
        # For every two characters we use 11 bits
        num_pairs = message_len // 2
        for _ in range(num_pairs):
            group = bit_str[pos:pos + 11]
            pos += 11
            num = int(group, 2)
            first_char = table[num // 45]
            second_char = table[num % 45]
            message += first_char + second_char
        # If the number of characters is odd, the last one is encoded on 6 bits
        if message_len % 2 == 1:
            group = bit_str[pos:pos + 6]
            pos += 6
            num = int(group, 2)
            message += table[num]
    
    elif encoding_type == "Numeric":
        # Groups of 3, 2 or 1 digit are processed
        i = 0
        while i < message_len:
            if message_len - i >= 3:
                group = bit_str[pos:pos + 10]
                pos += 10
                num = int(group, 2)
                # Se completează cu zerouri la stânga, dacă este necesar
                # Leading zeros are added if necessary
                digits = f"{num:03d}"
                message += digits
                i += 3
            elif message_len - i == 2:
                group = bit_str[pos:pos + 7]
                pos += 7
                num = int(group, 2)
                digits = f"{num:02d}"
                message += digits
                i += 2
            elif message_len - i == 1:
                group = bit_str[pos:pos + 4]
                pos += 4
                num = int(group, 2)
                message += str(num)
                i += 1

    return message
