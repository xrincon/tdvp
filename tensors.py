#/usr/bin/python

import numpy as np
from scipy import linalg
import cmath

np.set_printoptions(suppress=True, precision=3)

length = 8
d = 2
chi = 4

chir = [chi for n in range(length)]
chic = [chi for n in range(length)]
chir[0] = chic[length-1] = 1
print "chir =", chir
print "chic =", chic

MPS = [np.random.rand(chir[n], chic[n], d) for n in range(length)]
print "MPS =", MPS

#left-canonical orthonormalization
for n in range(length):
    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", n
    print "MPS shape", MPS[n].shape
    MPS[n] = np.transpose(MPS[n], (0, 2, 1))
    print "MPS shape", MPS[n].shape
    MPS[n] = MPS[n].reshape((chir[n] * d, chic[n]))
    print "MPS shape", MPS[n].shape

    Q, R = np.linalg.qr(MPS[n])

    MPS[n] = Q.copy()
    aux, chic[n] = MPS[n].shape

    i = np.random.randint(0, chic[n])
    j = np.random.randint(0, chic[n])
    dot = np.dot(Q[:,i], Q[:,j])
    print "dot =", i, j, round(dot, 10)

    print "MPS shape", MPS[n].shape
    MPS[n] = MPS[n].reshape((chir[n], d, chic[n]))
    print "MPS shape", MPS[n].shape
    MPS[n] = np.transpose(MPS[n], (0, 2, 1))
    print "MPS shape", MPS[n].shape

    print "Q[",n,"] =", Q
    print "R[",n,"] =", R

    if(n != length-1):
        print "shape =", MPS[n+1].shape
        MPS[n+1] = np.tensordot(R, MPS[n+1], axes=([1, 0]))
        chir[n+1], aux, aux = MPS[n+1].shape
        print "shape =", MPS[n+1].shape
    del Q, R, aux, i, j

#right-canonical orthonormalization
for n in range(length):
    ip = length-n-1
    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", ip
    print "MPS shape", MPS[ip].shape
    MPS[ip] = MPS[ip].reshape((chir[ip], chic[ip] * d))
    print "MPS shape", MPS[ip].shape

    MPS[ip] = np.conjugate(MPS[ip].T)
    print "MPS+ shape", MPS[ip].shape
    Q, R = np.linalg.qr(MPS[ip])

    Q = np.conjugate(Q.T)
    R = np.conjugate(R.T)

    MPS[ip] = Q.copy()
    chir[ip], aux = MPS[ip].shape

    i = np.random.randint(0, chir[ip])
    j = np.random.randint(0, chir[ip])
    dot = np.dot(Q[i,:], Q[j,:])
    print "dot =", i, j, round(dot, 10)

    print "MPS shape", MPS[ip].shape
    MPS[ip] = MPS[ip].reshape((chir[ip], chic[ip], d))
    print "MPS shape", MPS[ip].shape
    #MPS[n] = np.transpose(MPS[n], (0, 2, 1))
    #print "MPS shape", MPS[n].shape

    print "Q[",n,"] =", Q
    print "R[",n,"] =", R

    if(n != length-1):
        print "shape =", MPS[ip-1].shape
        MPS[ip-1] = np.tensordot(MPS[ip-1], R, axes=([1, 0]))
        print "shape =", MPS[ip-1].shape
        MPS[ip-1] = np.transpose(MPS[ip-1], (0, 2, 1))
        aux, chic[ip-1], aux = MPS[ip-1].shape
        print "shape =", MPS[ip-1].shape, chir[ip-1], chic[ip-1]
    del Q, R, aux

#exit()

print "chir =", chir
print "chic =", chic
print "MPS =", MPS

exit()


for n in range(length):
    print "MPS[",n,"] =", MPS[n]
    i = np.random.randint(0, chic[n])
    j = np.random.randint(0, chic[n])
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
