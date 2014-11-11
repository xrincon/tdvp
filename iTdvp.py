#!/usr/bin/python

import numpy as np
import scipy.sparse.linalg as spspla
import scipy.linalg as spla
import functools
import cmath

np.set_printoptions(suppress=True)#, precision=3)

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

    print "\nWARNING: powerMethod did not converge\n"
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

def buildLargeE(MPS):
    chir, chic, aux = MPS.shape
    AC = np.conjugate(MPS)
    AA = np.tensordot(MPS, AC, axes=([2,2]))
    AA = np.transpose(AA, (0, 2, 1, 3))
    AA = np.reshape(AA, (chir * chic, chir * chic))
    #print "AA", AA.shape, "\n", AA

    return AA

def getLargestW(MPS, dir):
    chir, chic, aux = MPS.shape

    if(dir == 'R'):
        linOpWrapped = functools.partial(linearOpForR, MPS)
    else:
        linOpWrapped = functools.partial(linearOpForL, MPS)

    linOpForEigs = spspla.LinearOperator((chir * chir, chic * chic), 
                                         matvec = linOpWrapped, 
                                         dtype='float64')
    omega, X = spspla.eigs(linOpForEigs, k=1, which='LR', tol=expS, 
                           maxiter=maxIter)
    X = X.reshape(chir, chic)

    phase = cmath.exp(-1j * cmath.phase(X[0,0]))
    X = phase * X
    if(np.fabs(X[1,0].imag) < expS): X = X.real

    return omega, X

def symmNormalization(MPS, chir, chic):
    """Returns a symmetric normalized MPS.

    This is really tricky business!

    AA = buildLargeE(MPS)
    omega, RX = spspla.eigs(AA, k=1, which='LR', tol=expS, 
                           maxiter=maxIter)
    print "w(1) =", omega, "\nRX\n", RX.reshape(chir, chic)

    AA = buildLargeE(MPS)
    omega, LX = spspla.eigs(np.transpose(np.conjugate(AA)), k=1, 
                            which='LR', tol=expS, maxiter=maxIter)
    print "w(1) =", omega, "\nLX\n", LX.reshape(chir, chic)
    """
    omega, R = getLargestW(MPS, 'R')
    print "wR", omega, "R\n", R


    R = spla.sqrtm(R)
    if(np.fabs(R[1,0].imag) < expS): R = R.real
    print "Rsqrt\n", R
    A = np.tensordot(MPS, R, axes=([1,0]))
    R = spla.inv(R)
    print "Rinv\n", R
    A = np.tensordot(R, A, axes=([1,0]))
    MPS = np.transpose(A, (0, 2, 1))


    omega, L = getLargestW(MPS, 'L')
    print "wL", omega, "L\n", L


    eval, evec = spla.eig(L)
    print "eval ", eval, "\n", evec
    A = np.tensordot(MPS, evec, axes=([1,0]))
    evec = np.transpose(np.conjugate(evec))
    MPS = np.tensordot(evec, A, axes=([1,0]))
    MPS = np.transpose(MPS, (0, 2, 1))


    eval = map(np.sqrt, map(np.sqrt, eval))
    A = np.tensordot(np.diag(eval), MPS, axes=([1,0]))
    eval = 1. / np.asarray(eval)
    MPS = np.tensordot(A, np.diag(eval), axes=([1,0]))
    MPS = np.transpose(MPS, (0, 2, 1))


    MPS /= np.sqrt(omega)
    if(np.fabs(MPS[0,0,0].imag) < expS): MPS = MPS.real
    #print "New MPS =", MPS.shape, "\n", MPS

    ######### CHECKING RESULT #########

    omega, L = getLargestW(MPS, 'L')
    print "wL", omega, "L\n", L

    omega, R = getLargestW(MPS, 'R')
    print "wR", omega, "R\n", R

    print "tr(R**2) =", np.trace(R**2), "tr(L**2) =", np.trace(L**2)

    return np.diag(R)

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

def getQHaaaaR(MPS, R, H, getE = False):
    """Returns either the energy density or the RHS of eq. for |K).
    """
    chir, chic, aux = MPS.shape
    AA = np.tensordot(MPS, MPS, axes=([1,0]))
    AAH = np.transpose(np.conjugate(AA), (2, 1, 0, 3))
    AAR = np.tensordot(AA, np.diag(R), axes=([2,0]))
    AARAAH = np.tensordot(AAR, AAH, axes=([3,0]))
    HAAAAR = np.tensordot(H, AARAAH, axes=([0,1,2,3], [1,2,3,5]))

    L = np.transpose(np.diag(np.conjugate(R)), (1, 0))

    if(getE):
        LHAAAAR = np.tensordot(L, HAAAAR, axes=([1,0]))
        return np.trace(LHAAAAR)
    else:
        Q = np.eye(chir, chic) - np.tensordot(np.diag(R), L, axes=([1,0]))
        QHAAAAR = np.tensordot(Q, HAAAAR, axes=([1,0]))
        print "Q\n", Q, "\nQHAAAAR\n", QHAAAAR
        return QHAAAAR.reshape(chir * chic)

def linearOpForK(MPS, R, K):
    """Returns ...

    Instead of defining QEQ as the regularized operator, we could 
    define QEQ = E - S = Q - |r)(l|; therefore avoiding more matrix 
    multiplications. Is this true?
    """
    chir, chic, aux = MPS.shape
    K = np.reshape(K, (chir, chic))
    L = np.transpose(np.diag(np.conjugate(R)), (1, 0))
    Q = np.eye(chir, chic) - np.tensordot(np.diag(R), L, axes=([1,0]))

    QK = np.tensordot(Q, K, axes=([1,0]))
    EQK = linearOpForR(MPS, QK.reshape(chir * chic))
    EQK = np.reshape(EQK, (chir, chic))
    QEQK = np.tensordot(Q, EQK, axes=([1,0]))
    tmp = K - QEQK

    return tmp.reshape(chir * chic)

def calcHmeanval(MPS, R, H):
    chir, chic, aux = MPS.shape
    QHAAAAR = getQHaaaaR(MPS, R, H)

    linOpWrapped = functools.partial(linearOpForK, MPS, R)
    linOpForBicg = spspla.LinearOperator((chir * chir, chic * chic), 
                                         matvec = linOpWrapped, 
                                         dtype='float64')
    K, info = spspla.bicgstab(linOpForBicg, QHAAAAR, tol=expS, 
                              maxiter=maxIter)
    if(info != 0): print "\nWARNING: bicgstab failed!\n"
    K = np.reshape(K, (chir, chic))

    print "Energy density =", getQHaaaaR(MPS, R, H, True)
    return K

def nullSpaceR(MPS, R):
    print "IN NULL SPACE R"
    RR = np.transpose(np.conjugate(MPS), (1, 0, 2))
    RR = np.tensordot(np.diag(map(np.sqrt, R)), RR, axes=([1,0]))
    chir, chic, aux = RR.shape

    RR = np.transpose(RR, (0, 2, 1))
    RR = np.reshape(RR, (chir * aux, chic))
    U, S, V = np.linalg.svd(RR, full_matrices=True)

    #dimS, = S.shape
    #extraS = np.zeros((chir * aux) - dimS)
    #Sp = np.append(S, extraS, 0)
    #maskp = (Sp < epsS) #try: np.select(...)

    mask = np.empty(chir * aux, dtype=bool)
    mask[:] = False; mask[chic:] = True
    VRdag = np.compress(mask, U, axis=1)

    RR = np.conjugate(np.transpose(RR))
    Null = np.tensordot(RR, VRdag, axes=([1,0]))
    Id = np.tensordot(VRdag.T, VRdag, axes=([1,0]))

    tmp = np.conjugate(VRdag.T)
    lpr, lmz = tmp.shape
    tmp = np.reshape(tmp, (lpr, chir, aux))
 
    print "mask =", mask, S, "\nU\n", U, "\nVRdag\n", VRdag, \
        "\nNull\n", Null, "\nVV+\n", Id, "\nVR =", tmp.shape
    del R, U, S, V, VRdag, Null, Id

    return tmp

def calcFs(MPS, C, R, K, VR):
    tmp1 = tmp2 = tmp3 = 0.
    VRdag = np.transpose(np.conjugate(VR), (1, 0, 2))
    Lsqrt = Rsqrt = np.diag(map(np.sqrt, R))
    Lsqrti = Rsqrti = np.diag(map(np.sqrt, 1./R))

    A = np.transpose(np.conjugate(MPS), (1, 0, 2))
    RsiVRdag = np.tensordot(Rsqrti, VRdag, axes=([1,0]))
    ARsiVRdag = np.tensordot(A, RsiVRdag, axes=([1,0]))
    RARsiVRdag = np.tensordot(np.diag(R), ARsiVRdag, axes=([1,0]))
    CRARsiVRdag = np.tensordot(C, RARsiVRdag, axes=([1,2,3], [0,3,1]))
    tmp1 = np.tensordot(Lsqrt, CRARsiVRdag, axes=([1,0]))
    #print tmp1

    RsVRdag = np.tensordot(Rsqrt, VRdag, axes=([1,0]))
    CRsVRdag = np.tensordot(C, RsVRdag, axes=([1,3], [0,2]))
    LCRsVRdag = np.tensordot(np.diag(R), CRsVRdag, axes=([1,0]))
    A = np.transpose(np.conjugate(MPS), (1, 0, 2))
    ALCRsVRdag = np.tensordot(A, LCRsVRdag, axes=([1,2], [0,1]))
    tmp2 = np.tensordot(Lsqrti, ALCRsVRdag, axes=([1,0]))
    #print tmp2

    RsiVRdag = np.tensordot(Rsqrti, VRdag, axes=([1,0]))
    KRsiVRdag = np.tensordot(K, RsiVRdag, axes=([1,0]))
    AKRsiVRdag = np.tensordot(MPS, KRsiVRdag, axes=([1,2], [0,2]))
    tmp3 = np.tensordot(Lsqrt, AKRsiVRdag, axes=([1,0]))
    #print tmp3

    tmp = tmp1 + tmp2 + tmp3

    return tmp

def getUpdateB(R, x, VR):
    Rsqrti = Lsqrti = np.diag(map(np.sqrt, 1./R))

    row, col, aux = VR.shape
    if(row*col == 0):
        row, row = Lsqrti.shape
        tmp = np.zeros((row, col, aux))
    else:
        VRRsi = np.tensordot(VR, Rsqrti, axes=([1,0]))
        VRRsi = np.transpose(VRRsi, (0, 2, 1))
        xVRRsi = np.tensordot(x, VRRsi, axes=([1,0]))
        tmp = np.tensordot(Lsqrti, xVRRsi, axes=([1,0]))

    print Lsqrti.shape, x.shape, VR.shape, tmp.shape

    return tmp

def doUpdateForA(MPS, B):
    """
    It does the actual update to the MPS state for given time step.

    The update is done according to the formula:
    A[n, t + dTau] = A[n, t] - dTau * B[x*](n),
    where dTau is the corresponding time step.
    """
    MPS -= dTau * B
    print "cmp shapes =", MPS.shape, B.shape

    return MPS



"""Main...
"""
d = 2
xi = 3
expS = 1e-12
maxIter = 200
dTau = 0.1

xir = xic = xi
theA = np.random.rand(xir, xic, d) - .5# + 1j * (np.random.rand(xir, xic, d) - .5)

theH = buildLocalH()
print "theH\n", theH.reshape(d*d, d*d)

I = 0
while (I != maxIter):

    theR = symmNormalization(theA, xir, xic)
    print "theR =", theR

    theC = buildHElements(theA, theH)
    print "theC =", theC.shape

    theK = calcHmeanval(theA, theR, theH)
    print "theK =", theK.shape
    exit()

    theVR = nullSpaceR(theA, theR)
    print "theVR =", theVR.shape

    theF = calcFs(theA, theC, theR, theK, theVR)
    print "theF =", theF.shape

    theB = getUpdateB(theR, theF, theVR)
    print "theB =", theB.shape

    doUpdateForA(theA, theB)

    I += 1
