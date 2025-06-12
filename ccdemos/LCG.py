import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation

# this is the structure of a LCG
def LCG(multiplicand, additive, seed):
    return ((multiplicand * seed) + additive) % pow(2, 32)

outputs = [0,0,0,0,0,0]
# get 5 outputs of numerical recipes' ranqd1 process
outputs[0] = LCG(1664525,1013904223, 1234)
for i in range(5):
    outputs[i+1] = LCG(1664525, 1013904223, outputs[i])

# NP's det sucks. it's a numeric algorithm (lol, who would've thought),
# so we're just gonna use the explicit formulization of a 3x3 determinant.
print(outputs)

detOne = outputs[0]*(outputs[2] - outputs[3]) - \
         outputs[1] * (outputs[1] - outputs[2]) + \
         (outputs[1] * outputs[3] - (outputs[2] * outputs[2]))
detTwo = outputs[1]*(outputs[3] - outputs[4]) - \
         outputs[2] * (outputs[2] - outputs[3]) + \
         (outputs[2] * outputs[4] - (outputs[3] * outputs[3]))
detThr = outputs[2]*(outputs[4] - outputs[5]) - \
         outputs[3] * (outputs[3] - outputs[4]) + \
         (outputs[3] * outputs[5] - (outputs[4] * outputs[4]))
print("Det1: " + str(detOne))
print("Det2: " + str(detTwo))
print("Det3: " + str(detThr))

# under the hood, this is just the euclidian algorithm or a variant
gcdOne = math.gcd(detOne, detTwo)
modulus = math.gcd(gcdOne, detThr)
print("Mod: " + str(modulus))
assert(modulus == pow(2, 32))

# now we test if (o1 - o0), m are coprime (GCD = 1)
coprime = math.gcd(outputs[1] - outputs[0], modulus)
print("Coprime?: " + str(coprime))
assert(coprime == 1)
# if this isn't true, solultions become moderately more complicated.
# for more information on this case, please see the paper
# "Cracking Chaos" in the main repository, section (3.1)
# Linear Congruential Generators
# However, in this case, we now find our multiplicand
multiplicand = ((outputs[2] - outputs[1]) * pow(outputs[1] - outputs[0], -1, modulus)) % modulus
print("A: " + str(multiplicand))
assert(multiplicand == 1664525)
# great, now we've recovered our
# 1: Modulus
# 2: Multiplier
# Now we're gonna have to turn our attention to our additive value, c
# this is a trivial algebra problem
# output = a * seed + c % m
# output_1 =  a * output_0 + c % m
# 889114580 = 1664525 * 3067928073 + c % 4294967296
intVal = (1664525 * 3067928073) % 4294967296
# 889114580 = intVal + c % 4294967296 -> 889114580 - intVal
additive = (889114580 - intVal) % 4294967296
print("C: " + str(additive))
assert(additive == 1013904223)
# from here we've completely recovered the structure of the generator
# all that's left of interest is completely recovering the seed
# output_0 = 3067928073
# output_0 = a * seed + c % m
# 3067928073 = 1664525 * seed + 1013904223 % m
# 3067928073 - 1013904223 % m = 1664525 * seed % m
seedVal = (((3067928073 - 1013904223) % modulus) * pow(1664525, -1, modulus)) % modulus
print("Seed: " + str(seedVal))
assert(seedVal == 1234)

# just for fun, we're gonna demonstrate a tendency towards the planes.
# we will use a significantly smaller modulus to showcase this effect
# as it can become very difficult to distinguish with a modulus like
# ranqd1's.

# a much worse LCG
# we chose this because the number of hyperplanes is governed by
# m^{1/k}, where k is the number of dimensions
# this should yield ~20 planes, against ranqd1's ~1625
# making the phenomenon much easier to observe
def hpLCG(multiplicand, additive, seed):
    return ((multiplicand * seed) + additive) % (pow(2, 13) - 1)

outputs = []
outputs.append(hpLCG(1234,420,4321))
for i in range(2999):
    outputs.append(float(hpLCG(1234,420, outputs[i])))
for i in range(len(outputs)):
    outputs[i] = outputs[i] / (pow(2, 13) - 1)
triplets = np.array([
    [outputs[i], outputs[i+1], outputs[i+2]] for i in range(len(outputs)-2)
])


# just plot stuff
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection="3d")
ax.scatter(triplets[:,0], triplets[:,1], triplets[:,2], s = 0.5, alpha = 1)

def rotate(angle):
    ax.view_init(elev=30, azim=angle)

ani = animation.FuncAnimation(fig, rotate, frames=np.arange(0, 360, 2), interval=50)

ax.set_xlim(0,1)
ax.set_ylim(0,1)
ax.set_zlim(0,1)
ax.set_xlabel("x_n")
ax.set_ylabel("x_{n+1}")
ax.set_zlabel("x_{n+2}")
ax.view_init(elev=20, azim=150)
plt.show()