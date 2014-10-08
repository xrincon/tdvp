#/usr/bin/python

import numpy as np
from scipy import linalg
import cmath

np.set_printoptions(suppress=True, precision=3)

length = 4
chi = 3
d = 2

MPS = [np.random.rand(chi*d*chi) for n in range(length)]
#MPS = [(n-(length-1)/2.0)*np.ones(chi*d*chi) for n in range(length)]
print MPS

for n in range(length):
    MPS[n] = MPS[n].reshape((chi * d, chi))
    Q, R = linalg.qr(MPS[n], mode='economic')
    MPS[n] = Q.copy()
    print "R[",n,"] =", R

    if(n != length-1):
        MPS[n+1] = MPS[n+1].reshape((chi, chi * d))
        MPS[n+1] = np.dot(R, MPS[n+1])
        MPS[n+1] = MPS[n+1].reshape((chi * d * chi))
    del Q, R

for n in range(length):
    print "MPS[",n,"] =", MPS[n]
    i = np.random.randint(0, chi)
    j = np.random.randint(0, chi)
    dot = np.dot(MPS[n][:,i], MPS[n][:,j])
    print "dot =", i, j, round(dot, 10)

"""
del R
print R

exit()

A = np.random.rand(chi*d*chi)
#A = A.astype(complex)
A = A.reshape((chi * d, chi))

Q, R = linalg.qr(A, mode='economic')

zrows = np.zeros((chi*d-chi, chi))
R = np.vstack((R, zrows))

print "A =", A#.shape
print "Q =", Q#.shape
print "R =", R#.shape

B = np.random.rand(chi*d*chi)
#B = A.astype(complex)
B = B.reshape((chi * d, chi))

print "B =",B

B = R * B

Q2, R2 = linalg.qr(B, mode='economic')

R2 = np.vstack((R2, zrows))

print "B =", B#.shape
print "Q2 =", Q2#.shape
print "R2 =", R2#.shape

C = np.random.rand(chi*d*chi)
#B = A.astype(complex)
C = C.reshape((chi * d, chi))

print "C =",C

C = R2 * C

Q3, R3 = linalg.qr(C, mode='economic')

R3 = np.vstack((R3, zrows))

print "C =", C#.shape
print "Q3 =", Q3#.shape
print "R3 =", R3#.shape

exit()

A = Q.copy()
"""
