from findMask import computeQrVersion

def is_eci(qr):
    rows = len(qr)
    cols = len(qr[0])
    bytes = str(qr[rows - 1][cols - 1]) + str(qr[rows - 1][cols - 2]) + str(qr[rows - 2][cols - 1]) + str(qr[rows - 2][cols - 2])
    
    if bytes == "0111":
        return True
    
    return False

def get_encoding_type(qr):
    rows = len(qr)
    cols = len(qr[0])
    
    if is_eci(qr):
        # bytes = str(qr[rows - 3][cols - 1]) + str(qr[rows - 3][cols - 2]) + str(qr[rows - 4][cols - 1]) + str(qr[rows - 4][cols - 2])
        # Find how many bits for ECI
        pass
    else:
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
    
def get_message_len(qr, encoding_type):
    n = len(qr)
    qr_version = ((n - 21) // 4) + 1 if n >= 21 else 1
    
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
    version = (n - 21) // 4 + 1

    # Matrix 'reserved' will be True on reserved (function) positions, False on data positions.
    reserved = [[False for _ in range(n)] for _ in range(n)]

    def mark_rect(r1, r2, c1, c2):
        for i in range(r1, r2 + 1):
            for j in range(c1, c2 + 1):
                reserved[i][j] = True

    # === 1. Mark function zones ===

    # 1.a. Finder patterns + separators
    # By standard, the modules in a 9x9 area are considered reserved at each corner
    # (except the bottom-right corner, where the separator is not repeated)
    mark_rect(0, 8, 0, 8)               # top-left
    mark_rect(0, 8, n - 8, n - 1)       # top-right
    mark_rect(n - 8, n - 1, 0, 8)       # bottom-left

    # 1.b. Timing patterns (horizontal and vertical lines)
    # The timing lines are on row 6 and column 6, outside the already reserved zones
    # (we use the limit: from 8 to n-9, if it exists)
    if n - 9 >= 8:
        mark_rect(6, 6, 8, n - 9)  # timing orizontal
        mark_rect(8, n - 9, 6, 6)  # timing vertical

    # 1.c. Format information
    # These are located near the finder patterns
    # – Vertical zone: column 8, rows 0..8 and rows n-8..n-1
    # – Horizontal zone: row 8, columns 0..8 and columns n-8..n-1
    for i in range(9):
        reserved[8][i] = True
        reserved[i][8] = True
    for j in range(n - 8, n):
        reserved[8][j] = True
    for i in range(n - 8, n):
        reserved[i][8] = True

    # 1.d. Alignment patterns (for versions >=2)
    if version >= 2:
        def get_alignment_centers(version, n):
            if version == 1:
                return []
            # Number of alignment patterns: floor(version/7) + 2.
            num_align = version // 7 + 2
            if num_align == 2:
                return [6, n - 7]
            # Step between centers (calculated so that the first is at 6 and the last at n-7)
            step = (n - 13) // (num_align - 1)
            centers = [6]
            for i in range(1, num_align - 1):
                centers.append(6 + i * step)
            centers.append(n - 7)
            return centers

        centers = get_alignment_centers(version, n)
        # For each pair (r, c) (alignment center), mark a 5x5 block (centered at (r, c)),
        # except when it overlaps with an eye.
        for r in centers:
            for c in centers:
                # If the center coincides with an eye, it is skipped.
                if (r, c) in ((6, 6), (6, n - 7), (n - 7, 6)):
                    continue
                r1, r2 = max(r - 2, 0), min(r + 2, n - 1)
                c1, c2 = max(c - 2, 0), min(c + 2, n - 1)
                mark_rect(r1, r2, c1, c2)

    # 1.e. Version information (for versions >=7)
    if version >= 7:
        # The version is encoded in two 3x6 areas:
        mark_rect(0, 5, n - 11, n - 9)  # top-right
        mark_rect(n - 11, n - 9, 0, 5)  # bottom-left

    # 1.f. Dark module
    dark_module_row = 4 * version + 8
    dark_module_col = 8
    if dark_module_row < n:
        reserved[dark_module_row][dark_module_col] = True

    # === 2. Extract bits from the data area, following the standard reading path ===

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



def get_message(qr, encoding_type, message_len):
    bits_list = extract_bits(qr)
    # Convert the list of bits (0 and 1) into a string of '0'/'1' characters
    bit_str = "".join(str(b) for b in bits_list)

    # After the specification, the first 4 bits are the mode indicator,
    # and the next bits are the length indicator (their number depends on the mode):
    n = len(qr)
    version = ((n - 21) // 4) + 1 if n >= 21 else 1
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


