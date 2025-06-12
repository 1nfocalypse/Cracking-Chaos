import random
# BlumBlumShub is a CSPRNG based on the hardness of the Quadratic Residuosity Problem
# It is defined as follows

def bbs(state, modulus):
    state = (state * state) % modulus
    return calcHammingWeight(state) % 2, state

def calcHammingWeight(number):
    c = 0
    while number:
        c+=1
        number &= number - 1
    return c

# However, to use it, we have to construct the modulus
# This is defined as N = PQ, where P, Q are primes of cryptographic size
# Additionally, it must follow that P, Q % 4 \equiv 3
# For further information, consult "Cracking Chaos" Section 4.4.1 "Blum-Blum-Shub"
# Notably, since we don't know primes of that size, we should generate our own.
# We will accomplish this via Miller-Rabin.

PRIME_SIZE = 2048
random.seed(31415)
def getRandomInt(PRIME_SIZE):
    retStr = "1"
    for i in range(PRIME_SIZE - 2):
        retStr += str(random.randint(0,1))
    return int(retStr + "1", 2)

def mr(number, rounds):
    r = 0
    s = number - 1
    while (s % 2 == 0):
        r += 1
        s >>= 1
    nm1precomp = number - 1
    for _ in range(rounds):
        a = random.randint(2, nm1precomp)
        x = pow(a, s, number)
        if x == 1 or x == nm1precomp:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, number)
            if x == nm1precomp:
                break
        else:
            return False
    return True

# now, we need to find two primes that are equivalent to 3 mod 4.
primes = []
while len(primes) != 2:
    num = getRandomInt(PRIME_SIZE)
    isPrime = mr(num, 40)
    if isPrime and num % 4 == 3:
        primes.append(num)

# now we have everything we need to use BBS!
# In practice, occasionally some additional tests are done
# to ensure a large cycle. But since this is just a showcase,
# we'll jump right into it by generating a 32 bit number in a
# secure manner.
print("Prime 1: " + str(primes[0]))
print("Prime 2: " + str(primes[1]))
modulus = primes[0] * primes[1]
OUT_BUF = [0] * 32
state = 123456789
for i in range(32):
    OUT_BUF[i], state = bbs(state, modulus)

num = 0
for bit in OUT_BUF:
    num = (num << 1) | bit
print(num)

# naturally, it can be pretty easy to understand why this algorithm isn't popular.
# but it's cool nonetheless!