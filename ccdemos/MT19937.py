import random
# This is one of the most complex generators discussed so far,
# the Mersenne Twister, specifically MT19937. It is also likely
# the most common PRNG in use today, being the default of many
# languages (including Python!). Regardless of its availability
# as the default, we will still work through a minimal
# implementation of the generator. We'll then use the default
# python MT19937 implementation, invert it, seed our construct
# with the outputted data, and begin to predict the outputs of
# Python's native MT19937 to drive home the point of just how
# easy this is to do.
random.seed(31415)

# we first specify the constants of MT19937
# 32 bit words
# 624 word state
# m = 397
# r = 31
# a = 0x9908B0DF
# u = 11
# s = 7
# b = 0x9D2C5680
# t = 15
# c = EFC60000
# l = 18

# basic state of the generator
state = [int(random.randint(0, 2**32-1)) for i in range(624)]
mti = 625

# this function covers both the twist in the if block in the
# case of the entire state being traversed in order to generate
# a new state, and the latter portion applies tempering.
# this tempering is what allows MT19937 to obtain equidistribution
# in up to 624 dimensions - without it, we see collapse a lot
# earlier. However, it's important to note that this is a
# trivially invertible relationship.
def generate(mti, state):
    mag01 = [0, 0x9908B0DF]
    if (mti >= 624):
        for i in range(624 - 397):
            y = (state[i]&0x80000000)|(state[i+1]&0x7FFFFFFF)
            state[i] = state[i+397] ^ (y >> 1) ^ mag01[y & 0x1]
        for i in range(624 - 397, 623):
            y = (state[i]&0x80000000)|(state[i+1]&0x7FFFFFFF)
            state[i] = state[i + (397 - 624)] ^ (y >> 1) ^ mag01[y & 0x1]
        y = (state[624-1]&0x80000000)|(state[0]&0x7FFFFFFF)
        state[624-1] = state[397-1] ^ (y >> 1) ^ mag01[y & 0x1]
        mti = 0

    y = state[mti]
    mti += 1
    y ^= (y >> 11)
    y ^= ((y << 7) & 0x9d2c5680) & 0xFFFFFFFF
    y ^= ((y << 15) & 0xEFC60000) & 0xFFFFFFFF
    y ^= (y >> 18)
    return y, mti
# let's print 10 outputs
for i in range(10):
    val, mti = generate(mti, state)
    print(hex(val))

# so now that we have our own implementation, lets
# get python's. We'll reseed to ensure state integrity.
random.seed(1234)
# this is the output after being modified by tempering
pyPuts = [random.getrandbits(32) for _ in range(624)]
# lets verify that our MT implementation works, first of all
state = list(random.getstate()[1])
mti = 0
ourPuts = []
for i in range(624):
    val, mti = generate(mti, state)
    ourPuts.append(val)
for i in range(624):
    assert(ourPuts[i] == pyPuts[i])
# we now know that our implementation works. Now let's reverse it to obtain state.
# we'll first work through the last transform of the tempering. We'll use a reduced
# example of:
# 1010 1011 >> 5
# 0000 0101 XOR
# 1010 1110 RES
# We see that the topmost bits are unaltered. So by performing the same operation, we
# can invert it.
# 1010 1110 >> 5
# 0000 0101 XOR
# 1010 1011 ORIG
def invLast(val):
    return val ^ (val >> 18)

# ok, now we need to worry about the left shift + masks.
# These are a bit more annoying.
# First of all, they are smaller than half the word, which
# would seem to imply that we cannot fully recover them consistently.
# plus, we have a mask that would seem to remove information. However,
# we are still able to reconstruct despite the mask, as the mask is
# actually only applied to our XOR value, which in turn can be
# reconstructed iteratively. This is achieved by moving through
# subsets of the string, reconstructing the XOR value, then masking it.

def invThird(val):
    result = val
    for i in range(0, 32, 15):
        mask = '0' * (17-i) + '1' * 15 + '0' * i
        mask = int(mask, 2)
        section = result & mask
        result ^= (section << 15) & 0xEFC60000
    return result

def invSecond(val):
    result = val;
    for i in range(0,32,7):
        mask = '0' * (25-i) + '1' * 7 + '0' * i
        mask = int(mask, 2)
        section = result & mask
        result ^= (section << 7) & 0x9d2c5680
    return result

# now we deal with the first transformation, which is very similar to how
# we dealt with the second and third, minus the final mask.
def invFirst(val):
    result = val
    for i in range(0,32,11):
        mask = '0' * i + '1' * 11 + '0' * (21-i)
        mask = int(mask, 2)
        section = result & mask
        result ^= section >> 11
    return result

def invTemper(val):
    return invFirst(invSecond(invThird(invLast(val))))

# now we'll invert the twist, and verify it matches the state
recovState = []
for i in range(624):
    recovState.append(invTemper(ourPuts[i]))
    assert(recovState[i] == state[i])

# since we've already established that by having the state, we can mirror
# the outputs, this in turn means that by collecting 624 outputs, we can
# then predict outcomes by simply seeding our generator with the recovered
# state, and then performing twists accordingly.