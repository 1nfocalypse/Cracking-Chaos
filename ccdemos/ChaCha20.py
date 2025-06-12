import random
# ChaCha20 is a great piece of engineering, through and through.
# It's a wonderfully simple ARX cipher that's proven itself
# extraordinarily resilient. It's used everywhere from protecting
# online comms to the Linux kernel. It would be a crime to not include
# it.

# we first begin by constructing a 16 DWORD matrix.
# naturally, don't actually use a mersenne twister to seed your
# CSPRNG. This is done for educational reasons.

random.seed(31415)
state = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,

         random.randint(0, pow(2,32)-1), random.randint(0, pow(2,32)-1),
         random.randint(0, pow(2,32)-1), random.randint(0, pow(2,32)-1),
         random.randint(0, pow(2,32)-1), random.randint(0, pow(2,32)-1),
         random.randint(0, pow(2,32)-1), random.randint(0, pow(2,32)-1),

         0,1,

         random.randint(0, pow(2,32)-1), random.randint(0, pow(2,32)-1)]

for val in state:
    print(hex(val), end=" ")
print("")

# lets break down this state quickly. The first 128 bits are a constant
# derived from "expand 32-byte k". The next block of 256 bits is the key.
# the next 64 bits are the counter, and the last 64 the nonce/IV.
# Don't reuse the nonce or you become vulnerable to cribdragging
# (And you will get owned if you're just hoping nobody guesses right)
# Additionally, this is Bernstein's original version with two 32 bit
# counter variables,

# now we get into the quarter round. ChaCha's a bit weird and breaks things
# down into quarter, even/odd rounds, and double rounds.
# this is where the ARX operations happen. For more information on ChaCha20,
# please reference "Cracking Chaos" section 4.1 "Stream Ciphers"
def QR(s,a,b,c,d):
    s[a] = (s[a] + s[b]) % 2**32
    s[d] ^= s[a];
    s[d] = rotl(s[d], 16)
    s[c] = (s[c] + s[d]) % 2**32
    s[b] ^= s[c]
    s[b] = rotl(s[b], 12)
    s[a] = (s[a] + s[b]) % 2**32
    s[d] ^= s[a]
    s[d] = rotl(s[d], 8)
    s[c] = (s[c] + s[d]) % 2**32
    s[b] ^= s[c]
    s[b] = rotl(s[b],7)

def rotl(val, rot):
    val &= 0xFFFFFFFF
    return (((val << rot) & 0xFFFFFFFF) | (val >> (32 - rot))) & 0xFFFFFFFF

# now we define the ChaCha double round, which is more akin to
# the basic block of the cipher.
def DR(state):
    s = list(state)
    # odd round
    QR(s, 0, 4, 8, 12)
    QR(s, 1, 5, 9, 13)
    QR(s, 2, 6, 10, 14)
    QR(s, 3, 7, 11, 15)
    # even round
    QR(s, 0, 5, 10, 15)
    QR(s, 1, 6, 11, 12)
    QR(s, 2, 7, 8, 13)
    QR(s, 3, 4, 9, 14)
    return s

# now we just perform 10 double rounds to get 20 rounds
tmpState = list(state)
for i in range(10):
    tmpState = DR(tmpState)
outputs = []
for i in range(len(state)):
    outputs.append((tmpState[i] + state[i]) % pow(2,32))
for output in outputs:
    print(hex(output),end=" ")
state = tmpState

# notably, this variant (the original published by Bernstein) does not have any test
# vectors. Or, at least any that I could find. However, there is an IETF variant.
# Which is actually used for TLS. That one has test vectors and is very similar
# to this version. However, without TV's, it's not feasible to easily validate
# this implementation. It should be correct, but exercise caution if you are
# using this as a reference (for some reason, why are you implementing this in python?)