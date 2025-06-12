import hashlib
import random
import math
# we're now going to walk through Hash_DRBG, one of NIST's generators.
# we will skip over the formal initialization requirements, since this
# is strictly a pedagogical demo and not intended to be seriously used.
# However, we will cover the entire structure of Hash_DRBG itself
# using SHA2. Any suitable hash algorithm may be used (i.e. SHA3,
# Streebog, not SHA1, MD5, etc.), and when done in conjunction with
# proper initialization, this construction is considered secure.

# lets initialize state
value = 0
constant = 0
reseed_counter = 0

# now we'll use a mersenne twister to generate our entropy input
# don't actually do this in practice - this is intended to simulate
# true RNG pulled from hardware. We're simply doing this because
# this is not a serious implementation and it's more convenient.
random.seed(1234)
entropy_input = random.randint(0, 2**256-1)
nonce = random.randint(0, 2**256-1)
# note, pers_string is optional and may be nothing
pers_string = b"Personal string."

seed_material = entropy_input << (512+(len(pers_string)*8)) | \
                nonce << (256+(len(pers_string)*8)) | \
                int.from_bytes(pers_string, byteorder='big')
seed_material = seed_material.to_bytes(math.ceil(seed_material.bit_length() / 8), byteorder='big')

# at this point, there's a NIST specific derivation you're supposed to use.
# We're just going to take the SHA256 of our seed material, since this is
# intended to showcase the structure rather than actually be used.
# The actual function is called Hash_df and can be found in NIST SP-800-90A.

# initialize our chosen hash function and derive our state.
# Reseed interval chosen arbitrarily.
v = int(hashlib.sha256(seed_material).hexdigest(),16)
c_mat = (0x00 << 256 | v)
constant = int(hashlib.sha256(c_mat.to_bytes(math.ceil(c_mat.bit_length() / 8), byteorder='big')).hexdigest(), 16)
reseed_counter += 1
reseed_interval = 16

# the generator is now initialized. We'll generate some output,
# then we'll go through the reseed/entropy injection procedure.
# we'll intentionally use a strange number - this is one of
# the benefits of Hash_DRBG, and to some extent, NIST's other
# DRBGs. Although, it can work to their detriment as well.
# For more information on the determinent, please refer to
# Cracking Chaos 4.2 "Block Ciphers in CTR Modes", specifically
# with regards to CTR_DRBG.

# We will also inject additional entropy, as Hash_DRBG allows, to
# show how that works. Additionally, at this point is when you
# check if you're due for entropy injection in a real implementation.
req_bits = 513
addl_input = b"Nobody expects more input!"
ad = 0x02 << (256+(len(addl_input)*8)) | v << (len(addl_input)*8) | int.from_bytes(addl_input, byteorder='big')
w = int(hashlib.sha256(ad.to_bytes(math.ceil(ad.bit_length() / 8), byteorder='big')).hexdigest(),16)
v = (v + 2) % (2**256)

# we've now injected more entropy into the system. Now,
# we obtain our output bits.
iterLim = int(math.ceil(req_bits / 256))
data = v
W = 0
for i in range(iterLim):
    w = int(hashlib.sha256(data.to_bytes(math.ceil(data.bit_length() / 8), byteorder='big')).hexdigest(), 16)
    W = (W << 256) | w
    data = (data + 1) % 2**256
num_bits = W.bit_length()
output = W >> (num_bits - req_bits)

# now advance the state
intVal = (0x03 << 264) | v
H = int(hashlib.sha256(intVal.to_bytes(math.ceil(intVal.bit_length() / 8), byteorder='big')).hexdigest(), 16)
V = (v + H + constant + reseed_counter) % 2**256
reseed_counter += 1

assert(output.bit_length() == 513)
# We've now generated 513 bytes from Hash_DRBG!
print(hex(output))
