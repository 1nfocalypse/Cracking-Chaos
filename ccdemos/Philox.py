# Philox is a weird-ish system, so lets work through this.
# We're going to be building out Philox4x32-10, arguably the most
# popular variant of the algorithm.
# We'll start with the barebones basics - constants.
MULT = [0xCD9E8D57, 0xD2511F53]
ROUND = [0x9E3779B9, 0xBB67AE85]

# Philox is a counter-based PRNG - it essentially operates like
# a block cipher in counter mode. This means we have some
# counter, c, and we "encrypt" the counter value
CTR = [0, 0, 0, 0]
KEYS = [20111115, 0]
# oh, fun thing about philox. The counter is backwards. very fun. truly.
# they don't really say that anywhere in the spec either... imagine how long
# that one took to figure out when I was doing this for the first time.

# now we're going to do the foundational functions of Philox, mulhi and mullo
def mulhi(a, b):
    return ((a * b) // pow(2,32)) % pow(2,32)

def mullo(a, b):
    return (a * b) % pow(2, 32)

# now the round function. This is where the actual primitives come into play.
# Philox makes use of two very popular cryptographic primitives: The SP-Net
# and the Feistel network. The round process, visualized, helps identify these
# processes.
# [a1 | a2 | a3 | a4]
# [a3 | a2 | a1 | a4]
# Above is the swap function performed every round between the intermediary
# positions and the new positions. We see that a1, a3 are swapped every round
# remniscient of a feistel network. a2, a4 remain in place (but are permuted).
# However, in the truly confusive/diffusive round functions, we see that values
# are shifted around between registers, i.e. a3 after being moved will influence
# the outcome of what is placed into a2's spot. This provides a portion of the
# diffusive effects of philox. For more information on Philox, please
# consult "Cracking Chaos" section 3.4 "Counter-based PRNGs"
def philox(counter, keys):
    OUTPUT = []
    for i in range(4):
        OUTPUT.append(counter[i])
    for j in range(10):
        INT = [OUTPUT[2], OUTPUT[1], OUTPUT[0], OUTPUT[3]]
        for k in range(2):
            OUTPUT[2*k] = mulhi(INT[2*k], MULT[k]) ^ ((keys[k] + (j * ROUND[k])) % pow(2, 32)) ^ INT[2 * k + 1]
            OUTPUT[(2*k)+1] = mullo(INT[2*k], MULT[k])
    return OUTPUT

# that's the heart of philox. All one needs to do is increment the counter,
# and that's it. Since this is a demo, we'll do it manually. But in a real
# implementation, usually you want something managing it.
# We'll double check our work with the test vectors:
tctr = [0,0,0,0]
tkeys = [0,0]
tvs = philox(tctr, tkeys)
for val in tvs:
    print(hex(val))

# those are them! Lets get 10000 values from philox.
# this is the C++ STL standard. We want 1955073260

for i in range(2500):
    values = philox(CTR, KEYS)
    if (i == 2499):
        print(values[3])
    CTR[0] += 1

# and we got it!