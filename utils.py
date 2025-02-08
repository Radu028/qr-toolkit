def get_qr_version(qr):
    n = len(qr)
    return ((n - 21) // 4) + 1 if n >= 21 else 1