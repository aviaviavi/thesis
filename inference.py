import math

def gamma(n):
    g = 7
    p = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    if n < 0.5:
        return math.pi / math.sin(n * math.pi) / gamma(1 - n)
    else:
        n -= 1
        x = p[0]
        for i in range(1, g+2):
            x += p[i] / (n + i)
        t = n + g + .5
        return math.sqrt(2 * math.pi) * (t ** (n + .5)) * math.exp(-t) * x

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

def gammaPDF(x, alpha, beta):
    if x < 0 or alpha < 0 or beta < 0:
        return None
    return ((beta ** alpha) * (x ** (alpha - 1)) * math.exp(-beta * x)) / gamma(alpha)

def likelihoodPP(t, k, lam):
    return math.exp(-lam * t) * ((lam * t) ** k) / factorial(k)

def inferPoissonHomogenous(k, t, priorAlpha, priorBeta):
    if t < 1 or priorAlpha < 0 or priorBeta < 0:
        return None
    bestParam = 0
    bestLikelihood = 0
    i = 0.001
    while i < 1:
        l = gammaPDF(i, priorAlpha, priorBeta)
        p = likelihoodPP(t, k, i)
        if (l * p) > bestLikelihood:
            bestLikelihood = l * p
            bestParam = i
        i += 0.001
    return bestParam

def inferPoissonHomogenousAnalytic(k, t, priorAlpha, priorBeta):
    return float((priorAlpha + k - 1)) / float((priorBeta + t))








