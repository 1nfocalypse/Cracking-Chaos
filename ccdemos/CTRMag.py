import random
# the following is the "Magma" cipher from the Russian GOST specifications.
# It is a very old cipher, hailing from Soviet times, and considered
# "fundamentally flawed" as a cryptographic primitive. However, it is very
# easy to implement and understand, hence why I have chosen to use it to
# illustrate the function of counter mode.
# NOTE: Never use Magma for serious cryptographic applications. It is selected
# here for its simplicity and ease of understanding - it is woefully insecure.
# As an extension, this CSPRNG lacks the "CS" portion of that acronym, and is
# not meant to be used in secure settings.

sbox = [
    [12,4,6,2,10,5,11,9,14,8,13,7,0,3,15,1],
    [6,8,2,3,9,10,5,12,1,14,4,7,11,13,0,15],
    [11,3,5,8,2,15,10,13,14,1,7,4,12,9,6,0],
    [12,8,2,1,13,4,15,6,7,0,10,5,3,14,9,11],
    [7,15,5,10,8,1,6,13,0,9,3,14,11,4,2,12],
    [5,13,15,6,9,2,12,10,11,7,8,1,4,3,14,0],
    [8,14,2,5,6,9,1,12,15,4,11,0,13,10,3,7],
    [1,7,14,13,0,5,8,3,4,15,10,6,9,12,11,2]
]

# input 32 bit word
# output 32 bit word
# perform substitution on each nibble
def sub(val):
    out = 0
    for i in reversed(range(8)):
        cur = (val >> (4*i)) & 0xF
        out <<= 4
        out ^= sbox[i][cur]
    return out

# left rotation for 32 bit number
def rotl(val, rot):
    val &= 0xFFFFFFFF
    return (((val << rot) & 0xFFFFFFFF) | (val >> (32 - rot))) & 0xFFFFFFFF

# input 256 bit subkey
# output list of 8 32 bit subkeys
# first 24 in order, last 8 in reverse
def keyGen(key):
    keys = []
    for i in reversed(range(8)):
        cur = (key >> (i*32)) & 0xFFFFFFFF
        keys.append(cur)
    for i in range(16):
        keys.append(keys[i % 8])
    for i in reversed(range(8)):
        keys.append(keys[i])
    return keys

def g(clear, key):
    return rotl(sub((clear + key) & 0xFFFFFFFF), 11)

# input list of keys, cleartext (counter)
# output 64 bit number (block size of Magma)
def encrypt(keys, clear):
    wkeys = list(keys)
    left = (clear >> 32) & 0xFFFFFFFF
    right = clear & 0xFFFFFFFF
    for i in range(31):
        left, right = right, left ^ g(right, keys[i])
    return (left ^ g(right, keys[-1])) << 32 | right

# now lets use the test vectors to make sure this is correct
# s box
assert(sub(0xFDB97531) == 0x2A196F34)
assert(sub(0x2a196f34) == 0xebd9f03a)
assert(sub(0xebd9f03a) == 0xb039bb3d)
assert(sub(0xb039bb3d) == 0x68695433)

# transform
assert(g(0x87654321, 0xfedcba98) == 0xfdcbc20c)
assert(g(0xfdcbc20c, 0x87654321) == 0x7e791a4b)
assert(g(0x7e791a4b, 0xfdcbc20c) == 0xc76549ec)
assert(g(0xc76549ec, 0x7e791a4b) == 0x9791c849)

# key scheduler
key = int('ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff', 16)
keys = keyGen(key)
chKeys = [0xffeeddcc, 0xbbaa9988, 0x77665544, 0x33221100, 0xf0f1f2f3, 0xf4f5f6f7, 0xf8f9fafb, 0xfcfdfeff]
for i in range(24):
    assert(keys[i] == chKeys[i%8])
for i in range(8):
    assert(keys[24+i] == chKeys[7-i])

# overall encryption
plaintext = 0xfedcba9876543210
out = encrypt(keys, plaintext)
assert(out == 0x4ee901e5c2d8ca3d)

# ok, magma works. Lets check out how CTR mode does.
# Magma needs a 256 bit key. We'll use the test vector one.
# it also needs a counter value - we'll use the test vector
# once again as our base. However, we must generate a
# nonce/IV. Let's do that right now...
random.seed(1234)
IV = random.randint(0, 2**64-1)
# now, we can combine the counter and IV in any invertible manner
# we'll just XOR
ctr = plaintext ^ IV
# now we'll output 16 values of Magma in CTR mode. In cryptographic
# context, this is what would be XOR'd with the cleartext to
# produce a keystream. However, for now it's treated as a PRNG.
for i in range(16):
    print(encrypt(keys,ctr))
    # invert the IV, increment, then recombine
    ctr ^= IV
    ctr += 1
    ctr ^= IV

# of particular note, we must consider the block width of
# the cipher we're using. Since we're using Magma, which
# has a block size of 64, it's advised to reseed every
# 2^32 outputs - all this means is that we need to
# introduce new entropy by that point, or we become
# trivially differentiable from random due to
# the nature of the block cipher being a bijection
# for further information on this, please see section
# 4.2 of Cracking Chaos, "Block Ciphers in CTR Modes"