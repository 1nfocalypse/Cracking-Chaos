# better reference: https://www.projectbullrun.org/dual-ec/documents/dual-ec-20150731.pdf

# these are the values for M-383
# p = modulus
# A = coefficient for x^2
# x/yVal = base point for the curve
p = (2 ** 383) - 187
A = 2065150
xVal = 12
yVal = 4737623401891753997660546300375902576839617167257703725630389791524463565757299203154901655432096558642117242906494

# Point class with projective coordinate added
class Point():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# ensures topmost bit is set - essential for montgomery ladder algorithm
def key_clamp(scalar):
    key = scalar % (2 ** 379)
    key = key + (2 ** 379)
    return key

# converts a given point's projective x coordinate to the affine coordinate
def convertAffine(point):
    return point.x * pow(point.z, -1, p) % p

# returns the value in the nomenclature of DUAL_EC_DRBG
def extractAffine(point):
    return convertAffine(point)

# returns the value of y^2 for a given x value
def retAffine(affineXCoord):
    return (pow(affineXCoord, 3) + A * (pow(affineXCoord, 2)) + affineXCoord)


def main():
    # this is our secret backdoor value
    secret = 255 | (2 ** 379)
    # Q will be our base point as recommended for M-383
    Q = Point(xVal, yVal, 1)
    # P will be our unexplained point
    P = LADDER(secret, Q)
    # this will be our seed for DUAL_EC_DRBG
    seed = 255123456789 | (2 ** 379)
    # we create an initial state by scalar mult of our seed against P
    initState = extractAffine(LADDER(seed, P))
    # our output is then the value of scalar mult against Q with the affine x coordinate from initState
    output = extractAffine(LADDER(initState, Q))
    # in order to invert it, we need to find y
    # to do this, we put the output value into the elliptic curve equation
    # this yields us with a value of y^2
    # since we're over a prime field, we can use tonelli-shanks to find a root of y
    # it doesn't actually matter which one - just as long as y is a quadratic residue
    yCoordOutput = _general_tonelli_shanks(retAffine(output), p)
    reconPt = Point(output, yCoordOutput, 1)
    # now, to enumerate state 2 as an observer
    # we're just going to use our reconstructed point, and multiply it against our secret linking Q,P
    recoveredState = extractAffine((LADDER(secret, reconPt)))
    assert(recoveredState == extractAffine(LADDER(initState, P)))
    print("Secret (backdoor):\t" + str(secret))
    print("Recovered State:\t" + str(recoveredState))
    print("Next State:\t\t\t" + str(extractAffine(LADDER(initState, P))))

# this is a constant op montgomery ladder
# specifically for M-383.
# it is not actually constant op due to python internals
def LADDER(scalar, initPt):
    x0 = xDBL(initPt)
    x1 = Point(initPt.x, initPt.y, initPt.z)
    for i in reversed(range(0, 379)):
        prevbit = (scalar >> (i + 1)) & 1
        curbit = (scalar >> i) & 1
        bit = prevbit ^ curbit
        vals = SWAP(bit, x0, x1)
        x0 = vals[0]
        x1 = vals[1]
        temp = x0
        x0 = xDBL(temp)
        x1 = xADD(temp, x1, initPt)
    vals = SWAP(scalar & 1, x0, x1)
    x0 = vals[0]
    x1 = vals[1]
    return x0

# constant operation swap algorithm to support the ladder
def SWAP(bit, pt1, pt2):
    tmpx = pt1.x
    tmpz = pt1.z
    pt1.x = (not bit) * pt1.x + (bit * pt2.x)
    pt1.z = (not bit) * pt1.z + (bit * pt2.z)
    pt2.x = (not bit) * pt2.x + (bit * tmpx)
    pt2.z = (not bit) * pt2.z + (bit * tmpz)
    return (pt1, pt2)

# differential addition over the curve's additive group
# constant op algorithm
def xADD(pt1, pt2, negpt):
    v0 = (pt1.x + pt1.z) % p
    v1 = (pt2.x - pt2.z) % p
    v1 = (v1 * v0) % p
    v0 = (pt1.x - pt1.z) % p
    v2 = (pt2.x + pt2.z) % p
    v2 = (v2 * v0) % p
    v3 = (v1 + v2) % p
    v3 = pow(v3, 2, p)
    v4 = (v1 - v2) % p
    v4 = pow(v4, 2, p)
    xfin = (negpt.z * v3) % p
    zfin = (negpt.x * v4) % p
    return Point(xfin, 1, zfin)

# pseudo-doubling algorithm over the curve's additive group
# constant op algorithm
def xDBL(pt):
    v1 = (pt.x + pt.z) % p
    v1 = pow(v1, 2, p)
    v2 = (pt.x - pt.z) % p
    v2 = pow(v2, 2, p)
    xdb = (v1 * v2) % p
    v1 = (v1 - v2) % p
    v3 = (((A + 2) // 4) * v1) % p
    v3 = (v3 + v2) % p
    zdb = (v1 * v3) % p
    return Point(xdb, 1, zdb)

# a legendre symbol. Returns 1 if a quadratic residue. We don't care if it's not.
# so we just kick back false.
def _legendre_symbol(num):
    return pow(num, (p-1)//2, p) == 1

# tonelli-shanks algorithm
# calculates the square root of a given quadratic residue
# over a prime characteristic field
def _general_tonelli_shanks(residue, field_char):
    if residue % field_char == 0:
        return 0
    if _legendre_symbol(residue) != 1:
        return None
    if (field_char % 4) == 3:
        return pow((residue % field_char), (field_char + 1)//4, field_char)
    Q = field_char - 1
    S = 0
    while Q % 2 == 0:
        S += 1
        Q //= 2
    z = 2
    while _legendre_symbol(z):
        z += 1
    M = S
    c = pow(z, Q, field_char)
    t = pow(residue, Q, field_char)
    R = pow(residue, (Q + 1)//2, field_char)
    while t != 1:
        i = 0
        tmp = t
        while tmp != 1:
            i += 1
            tmp = (tmp * tmp) % field_char
        pow2 = 2 ** (M - i - 1)
        b = pow(c, pow2, field_char)
        M = i
        c = (b * b) % p
        t = (t * b * b) % p
        R = (R * b) % p
    return R


if __name__ == "__main__":
    main()