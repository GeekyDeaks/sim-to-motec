# This code is released into the public domain with CC0.

def mask32(x):
    return x & 0xFFFFFFFF


def add32(x, y):
    return mask32(x + y)


def left_rotate(x, n):
    return mask32(x << n) | (x >> (32 - n))


# a, b, c, and d are indexes into the 16-word block
def quarter_round(block, a, b, c, d):
    block[b] ^= left_rotate(add32(block[a], block[d]), 7)
    block[c] ^= left_rotate(add32(block[b], block[a]), 9)
    block[d] ^= left_rotate(add32(block[c], block[b]), 13)
    block[a] ^= left_rotate(add32(block[d], block[c]), 18)


def salsa20_permute(block):
    for doubleround in range(10):
        quarter_round(block, 0, 4, 8, 12)  # column 1
        quarter_round(block, 5, 9, 13, 1)  # column 2
        quarter_round(block, 10, 14, 2, 6)  # column 3
        quarter_round(block, 15, 3, 7, 11)  # column 4
        quarter_round(block, 0, 1, 2, 3)  # row 1
        quarter_round(block, 5, 6, 7, 4)  # row 2
        quarter_round(block, 10, 11, 8, 9)  # row 3
        quarter_round(block, 15, 12, 13, 14)  # row 4


def words_from_bytes(b):
    assert len(b) % 4 == 0
    return [int.from_bytes(b[4 * i : 4 * i + 4], "little") for i in range(len(b) // 4)]


def bytes_from_words(w):
    return b"".join(word.to_bytes(4, "little") for word in w)


def salsa20_block(key, nonce, blocknum):
    # This implementation doesn't support 16-byte keys.
    assert len(key) == 32
    assert len(nonce) == 8
    assert blocknum < 2 ** 64
    constant_words = words_from_bytes(b"expand 32-byte k")
    key_words = words_from_bytes(key)
    nonce_words = words_from_bytes(nonce)
    # fmt: off
    original_block = [
        constant_words[0],  key_words[0],            key_words[1],       key_words[2],
        key_words[3],       constant_words[1],       nonce_words[0],     nonce_words[1],
        mask32(blocknum),   mask32(blocknum >> 32),  constant_words[2],  key_words[4],
        key_words[5],       key_words[6],            key_words[7],       constant_words[3],
    ]
    # fmt: on
    permuted_block = list(original_block)
    salsa20_permute(permuted_block)
    for i in range(len(permuted_block)):
        permuted_block[i] = add32(permuted_block[i], original_block[i])
    return bytes_from_words(permuted_block)


def salsa20_stream(key, nonce, length):
    output = bytearray()
    blocknum = 0
    while length > 0:
        block = salsa20_block(key, nonce, blocknum)
        take = min(length, len(block))
        output.extend(block[:take])
        length -= take
        blocknum += 1
    return output


def salsa20_xor(key, nonce, message):
    stream = salsa20_stream(key, nonce, len(message))
    return bytes(x ^ y for x, y in zip(message, stream))

# to be compatible with pySalsa
def Salsa20_xor(message, nonce, key):
    stream = salsa20_stream(key, nonce, len(message))
    return bytes(x ^ y for x, y in zip(message, stream))


def hsalsa20(key, input_bytes):
    # This implementation doesn't support 16-byte keys.
    assert len(key) == 32
    assert len(input_bytes) == 16
    constant_words = words_from_bytes(b"expand 32-byte k")
    key_words = words_from_bytes(key)
    input_words = words_from_bytes(input_bytes)
    # fmt: off
    block = [
        constant_words[0],  key_words[0],       key_words[1],       key_words[2],
        key_words[3],       constant_words[1],  input_words[0],     input_words[1],
        input_words[2],     input_words[3],     constant_words[2],  key_words[4],
        key_words[5],       key_words[6],       key_words[7],       constant_words[3],
    ]
    # fmt: on
    salsa20_permute(block)
    outputs = [block[i] for i in [0, 5, 10, 15, 6, 7, 8, 9]]
    return bytes_from_words(outputs)


def xsalsa20_stream(key, nonce, length):
    # This implementation doesn't support 16-byte keys.
    assert len(key) == 32
    assert len(nonce) == 24
    derived_key = hsalsa20(key, nonce[:16])
    return salsa20_stream(derived_key, nonce[16:], length)


def xsalsa20_xor(key, nonce, message):
    stream = xsalsa20_stream(key, nonce, len(message))
    return bytes(x ^ y for x, y in zip(message, stream))
