import math
from scipy.special import gamma
from scipy.special import gammaln
import matplotlib.pyplot as plt
import scipy
import random

hyps = [[.001, 1.0], [50.0, 1.0]]
maxRate = 10

def coin_flip(x):
    return 1 if random.random() < x else 0

def frange(x, y, z):
    while x < y:
        yield x
        x += z

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

def gammaPDF(x, alpha, beta):
    if x < 0 or alpha < 0 or beta < 0:
        return None
    out = ((beta ** alpha) / gamma(alpha)) * (x ** (alpha - 1)) * math.exp(-beta * x)
    return out

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

def inferPoissonHomogenousAnalytic(t, k, priorAlpha, priorBeta):
    return float((priorAlpha + k - 1)) / float((priorBeta + t))

def posteriorProb(lam, t, k, a, b):
    return gammaPDF(lam, a+k, b+t) 

def postProbCalc(l, t, k, a, b):
    return (((b+t) ** (a+k)) / gamma(a+k))  * l**(a+k-1) * math.exp(-l * (b+t))

def friends(t, k, maxRate):
    return bestHyp(t, k, hyps, maxRate)

def bestHyp(t, k, hyps, maxRate):
    maxProb = None 
    bestHyp = None
    for h in hyps:
        p = integralGammaPDF(maxRate, h[0]+k, h[1]+t) - integralGammaPDF(.0000001, h[0]+k, h[1]+t)
        print h, p, maxProb, bestHyp
        if p >= maxProb or maxProb is None:
            bestHyp = h
            maxProb = p
    return bestHyp, maxProb 

def integralGammaPDF(t, k, a, b):
    #print t, k, a, b
    out = gamma(k+a)/gamma(a) * ((b ** a) / (t+b)**(k+a))
    #print out
    return out

def sumGammaPDF(maxRate, a, b):
    total = 0
    for l in frange(.01, maxRate, .01):
        total += gammaPDF(l, a, b)
    return total

def graphBeliefOnFixedT(t, hyps):
    pointsX = []
    pointsY = []
    pointsK = []
    for k in range(1,100):
        h0 = integralGammaPDF(t, k, hyps[0][0], hyps[0][1])
        h1 = integralGammaPDF(t, k, hyps[1][0], hyps[1][1])
        pointsX.append(k)
        pointsY.append(h1/(h0+h1))
        pointsK.append(h0/(h0+h1))

    print pointsY, pointsK
    plt.plot(pointsX, pointsY, label="friends")
    plt.plot(pointsX, pointsK, label="not friends")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
       ncol=2, mode="expand", borderaxespad=0.)
    plt.show()


# p(d | a, theta)
def likelihoodPosterior(d, a0, b0, a1, b1):
    probFriends = .5 # hardcoded
    p = None
    for x_i in d:
        t = x_i[0]
        k = x_i[1]
        temp = (integralGammaPDF(t, k, a0, b0) * (1 - probFriends)) + (integralGammaPDF(t, k, a1, b1) * probFriends) #we will assume uniform dist on all priors
        p = temp * p if p else temp
    return p

def priorOnPriors(a0, b0, a1, b1):
    return 1.0 / (1.0 - ((a0*b0)/(a1*b1)))

def metropolisHastings(data):
    print hyps
    num_bars = 30
    max_iter = 10000
    num_convos = 3
    a0 = hyps[0][0]
    theta0 = hyps[0][1]
    a1 = hyps[1][0]
    theta1 = hyps[1][1]
    iterations = 0

    current_samples = [a0, theta0, a1, theta1]
    samples_z = [ [] for _ in range(num_convos)]
    l = likelihoodPosterior(data, a0, theta0, a1, theta1)
    p = priorOnPriors(a0, theta0, a1, theta1)
    current_prob = l * p

    a0 = []
    a1 = []
    theta0 = []
    theta1 = []

    done = False
    while not done:
        next_samples = [scipy.random.normal(param) for param in current_samples]
        next_samples = map(lambda x: max(x, .01), next_samples)
        next_prob = apply(likelihoodPosterior, [data] + next_samples) * apply(priorOnPriors, next_samples)
        a = next_prob / current_prob
        rand = random.random()
        if a > 1 or rand < a:
            #print a, rand
            current_samples = next_samples
            current_prob = next_prob
            #if iterations > 100 and iterations % 2 == 0: #burn in of 100 and only take every 5. does that go here, or two lines up?
            if iterations > 100: #burn in of 100 and only take every 5. does that go here, or two lines up?
                a0.append(current_samples[0])
                a1.append(current_samples[1])
                theta0.append(current_samples[2])
                theta1.append(current_samples[3])

                for i in range(len(samples_z)):
                    samples_z[i].append(sample_z(*[data[i][0], data[i][1]] + current_samples))

            #print 'new'
        iterations += 1
        if iterations > max_iter:
            done = not done

    for i in range(len(samples_z)):
        p = float(sum(samples_z[i]))/len(samples_z[i])
        samples_z[i] = [1-p, p]
        print samples_z[i]

    #plt.hist(a0, num_bars, normed=1)
    #plt.title("a0")
    #plt.show()
    #plt.hist(theta0, num_bars, normed=1)
    #plt.title("theta0")
    #plt.show()
    #plt.hist(a1, num_bars, normed=1)
    #plt.title("a1")
    #plt.show()
    #plt.hist(theta1, num_bars, normed=1)
    #plt.title("theta1")
    #plt.show()

    plt.bar([0, .5], samples_z[0], width=.5)
    plt.title("z0")
    plt.xticks([.33, .66], ('not friends', 'friends'))
    plt.show()
    plt.bar([0, .5], samples_z[1], width=.5)
    plt.title("z1")
    plt.xticks([.33, .66], ('not friends', 'friends'))
    plt.show()
    plt.bar([0, .5], samples_z[2], width=.5)
    plt.title("z2")
    plt.xticks([.33, .66], ('not friends', 'friends'))
    plt.show()
    #return current_samples


def sample_z(t, k, a0, theta0, a1, theta1):
    l_h0 = integralGammaPDF(t, k, a0, theta0)
    l_h1 = integralGammaPDF(t, k, a1, theta1)
    p_h1 = l_h1 / (l_h0 + l_h1)
    #print p_h1
    return coin_flip(p_h1)

print metropolisHastings([[5, 1], [5, 15], [5, 55]])
