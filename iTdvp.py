#!/usr/bin/python

import numpy as np
import scipy.sparse.linalg as spspla
import scipy.linalg as spla
import functools
import cmath

np.set_printoptions(suppress=True)#, precision=3)

def realFunc(x, y, z):
    print "x =", x
    print "y =", y
    print "z =", z

def callIt(A, B, C):
    funcWrapped = functools.partial(realFunc, A, B)
    funcWrapped(C)

################################################################

def powerMethod(MPS, dir):
    eval = 1234.5678
    chir, chic, aux = MPS.shape
    X = np.random.rand(chir * chic) - .5

    for q in range(maxIter):
        if(dir == 'R'): Y = linearOpForR(MPS, X)
        else: Y = linearOpForL(MPS, X)

        Y = np.reshape(Y, (chir, chic))
        YH = np.transpose(np.conjugate(Y), (1, 0))
        YHY = np.tensordot(YH, Y, axes=([1, 0]))
        norm = np.sqrt(np.trace(YHY))
        X = Y / norm

        if(np.abs(eval - norm) < expS): return norm, X
        else: eval = norm

    return -1, np.zeros(chir, chic)

def linearOpForR(MPS, R):
    chir, chic, aux = MPS.shape
    R = np.reshape(R, (chir, chic))
    AR = np.tensordot(MPS, R, axes=([1,0]))
    AH = np.transpose(np.conjugate(MPS), (1, 0, 2))
    ARAH = np.tensordot(AR, AH, axes=([1,2], [2,0]))

    return ARAH.reshape(chir * chic)

def linearOpForL(MPS, L):
    chir, chic, aux = MPS.shape
    L = np.reshape(L, (chir, chic))
    LA = np.tensordot(L, MPS, axes=([1,0]))
    AH = np.transpose(np.conjugate(MPS), (1, 0, 2))
    AHLA = np.tensordot(AH, LA, axes=([1,2], [0,2]))

    return AHLA.reshape(chir * chic)

def symmNormalization(MPS, chir, chic):
    """Returns a symmetric normalized MPS.

    This is really tricky business!
    """
    AH = np.transpose(np.conjugate(MPS), (1, 0, 2))
    AA = np.tensordot(MPS, AH, axes=([2,2]))
    AA = np.transpose(AA, (0, 1, 3, 2))
    AA = np.transpose(AA, (0, 2, 1, 3))
    AA = np.reshape(AA, (chir * chic, chir * chic))
    ##print "AA =\n", AA

    omega, R = spspla.eigs(AA, k=1, which='LR', tol=expS, 
                           maxiter=maxIter)
    print "w(1) =", omega
    ##Aval, Avec = spla.eig(AA)
    ##print Aval

    linOpWrapped = functools.partial(linearOpForR, MPS)
    linOpForEigs = spspla.LinearOperator((chir * chic, chir * chic), 
                                         matvec = linOpWrapped)
    omega, R = spspla.eigs(linOpForEigs, k=1, which='LR', tol=expS, 
                           maxiter=maxIter)
    R = R.reshape(chir, chic)
    print "w(1) =", omega, "\nR\n", R
    ##omega, R = powerMethod(MPS, dir='R')
    ##print "w(1) =", omega, "\nR\n", R


    R = spla.sqrtm(R)
    A = np.tensordot(MPS, R, axes=([1,0]))
    R = spla.inv(R)
    A = np.tensordot(R, A, axes=([1,0]))
    MPS = np.transpose(A, (0, 2, 1))


    linOpWrapped = functools.partial(linearOpForL, MPS)
    linOpForEigs = spspla.LinearOperator((chir * chic, chir * chic), 
                                         matvec = linOpWrapped)
    omega, L = spspla.eigs(linOpForEigs, k=1, which='LR', tol=expS, 
                           maxiter=maxIter)
    L = L.reshape(chir, chic)
    print "w(1) =", omega, "\nL\n", L
    ##omega, L = powerMethod(MPS, dir='L')
    ##print "w(1) =", omega, "\nL\n", L


    eval, evec = spla.eig(L)
    print eval, "\n", evec
    A = np.tensordot(MPS, evec, axes=([1,0]))
    evec = np.conjugate(evec.T)
    MPS = np.tensordot(evec, A, axes=([1,0]))
    MPS = np.transpose(MPS, (0, 2, 1))


    eval = map(np.sqrt, map(np.sqrt, eval))
    A = np.tensordot(np.diag(eval), MPS, axes=([1,0]))
    eval = 1/np.asarray(eval)
    MPS = np.tensordot(A, np.diag(eval), axes=([1,0]))
    MPS = np.transpose(MPS, (0, 2, 1))

    MPS /= np.sqrt(omega)
    print "New MPS =", MPS.shape

    omega, L = powerMethod(MPS, dir='L')
    print "chk =", omega, "\nL\n", L

    omega, R = powerMethod(MPS, dir='R')
    print "chk =", omega, "\nR\n", R

    return np.diag(map(np.abs, L))

def buildLocalH():
    """Builds local hamiltonian (d x d)-matrix.

    Returns local hamiltonian for a translation invariant system.
    The local H is a (d, d, d, d)-rank tensor.
    """
    localH = np.zeros((d, d, d, d))
    localH[0,0,0,0] = localH[1,1,1,1] = 1./4.
    localH[0,1,0,1] = localH[1,0,1,0] = 1./4.
    localH[1,0,0,1] = localH[0,1,1,0] = 1./2.

    return localH

def buildHElements(MPS, H):
    """Builds the matrix elements of the hamiltonian.

    Returns a tensor of the form C[a, b, s, t].
    """
    AA = np.tensordot(MPS, MPS, axes=([1,0]))
    tmp = np.tensordot(H, AA, axes=([2,3], [1,3]))
    C = np.transpose(tmp, (2, 3, 0, 1))

    return C


"""Main...
"""
length = 4
d = 2
xi = 3
expS = 1e-12
maxIter = 200

xir = xic = xi
theA = np.random.rand(xir, xic, d) - .5

theH = buildLocalH()
print "theH\n", theH.reshape(d*d, d*d)

theR = symmNormalization(theA, xir, xic)
print "theR =", theR

theC = buildHElements(theA, theH)
print "theC =", theC.shape

calcHmeanval(theA, theR, theH)