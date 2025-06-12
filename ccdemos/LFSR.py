import numpy as np
from sympy import Matrix, GF, pprint

# we will be utilizing a Fibonacci LFSR for demonstration purposes.
# a better choice in software is a XOR-Shift LFSR.
# but this is the most "basic" version, so it's interesting for pedagogical reasons.

# 8 bit long LFSR with a seed of 00110101
# of the form
#      1  x  x2 x3 x4 x5 x6 x7
REG = [0, 0, 1, 1, 0, 1, 0, 1]
# we will pick the primitive polynomial
# x^7 + x^6 + 1, making the last two positions of the register our taps

# 32 bit output buffer
OUT_BUF = []
# we now define a function to advance state
def adv(REG):
    OUT_BIT = REG[7]
    NEW_BIT = REG[7] ^ REG[6]
    REG.insert(0, NEW_BIT)
    REG.pop(8)
    return OUT_BIT

# just to see this in action
for i in range(32):
    OUT_BUF.append(adv(REG))
print(OUT_BUF)
num = 0
for bit in OUT_BUF:
    num = (num << 1) | bit
print("Our generated number: " + str(num))

# first, we'll discuss a means of detecting the length of a LFSR and inverting.
# This is the naive, extremely inefficient method.
# we'll use sympy for this, because numpy is numerical and will introduce error.
# we'll pretend we don't know the size of the register and guess it's a 7 bit
# register. We'll construct a Hankel matrix as follows, and test.
sbs = [[OUT_BUF[i+j] for i in range(7)]
       for j in range(7)]
sbssp = Matrix(sbs)
print("7x7 Hankel Matrix")
pprint(sbssp)
rank = sbssp.rank(iszerofunc=lambda x: x % 2 == 0)
print("Rank of 7x7: " + str(rank))
# ok, we got a full rank matrix. This means it's either 7 bits or larger.
print("")
# Let's try 10x10
fbf = [[OUT_BUF[i+j] for i in range(10)]
       for j in range(10)]
fbfsp = Matrix(fbf)
print("10x10 Hankel Matrix")
pprint(fbfsp)
rank = fbfsp.rank(iszerofunc=lambda x: x % 2 == 0)
print("Rank of 10x10: " + str(rank))
# we find that we do not have a full rank matrix, rather one of rank 8,
# denoting this probabably comes from a LFSR of length 8.

# so now we worry about inversion.
# inverting a LFSR is done with an algorithm called Berlekamp-Massey
# it essentially will attempt to reconstruct the polynomial guiding the
# output of the LFSR such that it is the shortest polynomial possible
# if you get back a short polynomial for a fairly long sequence, it's
# usually a good sign that you've inverted the generator. For more
# information, consult "Cracking Chaos" section 3.2.

def calcDisc(s, C, L, N):
    d = s[N]
    for i in range(1, L + 1):
        d ^= C[i] & s[N - i]
    return d

def polyAdd(a, b):
    length = max(len(a), len(b))
    a += [0] * (length - len(a))
    b += [0] * (length - len(b))
    return [a[i] ^ b[i] for i in range(length)]

def shift(poly, k):
    return [0] * k + poly

def berlekamp_massey(s):
    n = len(s)
    C = [1]
    B = [1]
    L = 0
    m = -1
    N = 0
    while N < n:
        d = calcDisc(s, C, L, N)
        if d == 1:
            T = C[:]
            C = polyAdd(C, shift(B, N - m))
            if L <= N // 2:
                L = N + 1 - L
                B = T
                m = N
        N += 1
    return L, C

length, poly = berlekamp_massey(OUT_BUF)

# this tells us both the size of the buffer and
# the feedback polynomial. We can observe that
print("Register size: " + str(length))
print("Feedback polynomial coefficients:")
print(poly)

# we correctly find it to be an 8 bit register
# and a polynomial of the form 1 + x^6 + x^7
# thus correctly deriving the structure of the polynomial
# and given the seed is now known to be the first
# 8 bits (the size of the register), we can invert
# the generator by pulling the 8 MSB off of the 32 bit int
# that we generated.
msbnum = (num >> 24) & 0xFF
# this, in binary, should be our seed (in reverse)
print(bin(msbnum))
# indeed, we find it to be 10101100, which reversed,
# matches our initial seed of 0, 0, 1, 1, 0, 1, 0, 1
# Note: This is raw output. Real world designs may alter
# the output of a LFSR to frustrate this means of attack.