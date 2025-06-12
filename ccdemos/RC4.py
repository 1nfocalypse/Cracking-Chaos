import random
from collections import Counter
import matplotlib.pyplot as plt

# first we do the key scheduling algorithm
# we'll pick a nice 128 bit key
key = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
S = []
for i in range(256):
    S.append(i)
j = 0
for i in range(256):
    j = (j + S[i] + key[i % 16]) % 256
    S[i], S[j] = S[j], S[i]

# for example, we'll generate 16 bytes of output.
i = 0
j = 0
outBuf = []
for k in range(16):
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    S[i], S[j] = S[j], S[i]
    t = (S[i] + S[j]) % 256
    outBuf.append(S[t])
print("Sample 16 bytes: " + str(outBuf))

# we'll now set up the differentiability showcase. we'll use a Mersenne Twister to generate
# 1000 unique 128 bit keys, then we'll run them through RC4. We should see a tendency for
# the second output to be 0.
# NOTE: NEVER USE A MERSENNE TWISTER FOR ACTUAL KEY GENERATION
random.seed(1234)
keyList = [[random.randint(0,255) for _ in range(16)] for _ in range(100000)]
# Great, now that we have our keys, lets run the algorithm on each one.
# we'll return the value of the second output for each key
# we should find that 0 is a common second word

def RC4(key):
    S = []
    for i in range(256):
        S.append(i)
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % 16]) % 256
        S[i], S[j] = S[j], S[i]
    i = 0
    j = 0
    final = 0
    for k in range(2):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = (S[i] + S[j]) % 256
        final = S[t]
    return final

secBytes = [RC4(key) for key in keyList]
counts = Counter(secBytes)

plt.bar(range(256), [counts[i] for i in range(256)], color='gray')
plt.xlabel('Second Output Byte')
plt.ylabel('Frequency')
plt.title('RC4 Second Byte Distribution over 100000 Keys')
plt.axhline(len(secBytes)/256, color='red', linestyle='--', label='Uniform Expectation')
plt.legend()
plt.show()
print("Number of 0's: " + str(counts[0]))
# We get 809 counts of 0 out of 100,000 keys
# While this doesn't seem that bad, it's about twice
# the expected number, throwing off the distribution
# It's been found that given 200 RC4 streams,
# one is able to differentiate from a random stream and
# RC4 > 64% of the time based on this phenomena.
# For more information, see "Cracking Chaos" Section
# 4.1: "Stream Ciphers"