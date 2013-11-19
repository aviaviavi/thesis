function hawkesProcess(baseRate, maxRate, name) {
    this.name = name;
	this.baseRate = baseRate;
	this.events = [];
	this.excitors = [];
	this.maxRate = maxRate;

	this.currentRate = function(t) {
		rate = this.baseRate;
		for (var i = 0; i < this.excitors.length; i++) { 
			process = this.excitors[i][0];
			theta = this.excitors[i][2];
            beta = this.excitors[i][3];
			for (var j = 0; j < process.events.length; j++) { 
                if (process.events[j] > t) break;
				rate += this.decay(theta, beta, t, process.events[j]);
			}
		} 
		//console.log(rate);
		return Math.min(rate, this.maxRate);
	}

	this.excitedBy = function(otherHP, decayFunct, theta, beta) {
		this.excitors.push([otherHP, decayFunct, theta, beta]);
	}

	/*theta - decay parameter
	  t - current time
	  s - event to excite */
	this.decay = function(theta, beta, t, s) {
		return beta * Math.exp(-theta * (t - s))
	}

}

//ticks per hour is an int. 1 will always be our finest granularity, and we will scale our time by how many ticks will be in 
//any given unit of time.
function simulate(allProcesses, ticksPerHour) {
	var t = 0;
	var numEvents = 0;
	var process;
	maxTime = 3600 * 24 * 7;
	while (t < maxTime) {
		for (var p = 0; p < allProcesses.length; p++) {
			process = allProcesses[p];
			//TODO: this needs to be fixed.
			if (Math.random() < (process.currentRate(t) / ticksPerHour)) {
				process.events.push(t);
				numEvents++;
				break;
			}
		}
        t++;
	}
}

function sortEvents(processes) {
    var sortedEventsLabeled = [],
        sortedEvents = [];

    var currTime;
    for (var i = 0; i < processes.length; i++) {
        var p = processes[i];
        for (var j = 0; j < p.events.length; j++) {
            currTime = p.events[j];
            sortedEventsLabeled.push([currTime, p.name]);
            sortedEvents.push(currTime);
        }
    }
    sortedEventsLabeled.sort(function(a, b) {return a[0] - b[0];}); 
    sortedEvents.sort(function(a, b) {return a - b;});

    return [sortedEvents, sortedEventsLabeled];
}

//given an object of form {from : {to : {trans: p, wait: t}}}
//normalize to a probability summing to one for each 'from'
function normalizeTransitions(trans_dist) {
    for (start in trans_dist) {
        total = 0;
        for (end in trans_dist[start]) {
           total += trans_dist[start][end]['trans'];
        } for (end in trans_dist[start]) {
           trans_dist[start][end]['trans'] /= total;
        } 
    }
}

//get transition distribution, wait time distribution
//needs all processes and labeled events
function getTransitionDist(allProcesses, events) {
    var trans_dist = {};
    for (var x = 0; x < allProcesses.length; x++) {
        trans_dist[allProcesses[x].name] = {};
        for (var y = 0; y < allProcesses.length; y++) {
            trans_dist[allProcesses[x].name][allProcesses[y].name] = {};
            trans_dist[allProcesses[x].name][allProcesses[y].name]['trans'] = 0;
            trans_dist[allProcesses[x].name][allProcesses[y].name]['wait'] = 0;
        }
    }

    for (var i = 1; i < events.length; i++) {
        from = events[i-1][1];
        to = events[i][1];
        delta = events[i][0] - events[i-1][0];
        trans_dist[from][to]['trans']++;
        if (trans_dist[from][to]['wait'] === 0) //we haven't set this wait time yet
            trans_dist[from][to]['wait'] = delta;
        else
            trans_dist[from][to]['wait'] = (trans_dist[from][to]['wait'] + delta) / trans_dist[from][to]['trans'];
    }
    return trans_dist;
}

    
function inferParameters(allProcesses, priorThetas, priorBetas) {
    if ((priorThetas.length != priorBetas.length) || (priorThetas.length != (allProcesses.length * (allProcesses.length - 1)))) {
        console.log("input error, num prior parameters is incorrect for the number of nodes");   
        return 0;
    }
        
    events = sortEvents(allProcesses)[1];
    trans_dist = getTransitionDist(allProcesses, events); 
    normalizeTransitions(trans_dist);
}

function gamma(n) {  // accurate to about 15 decimal places
    //some magic constants 
    var g = 7, // g represents the precision desired, p is the values of p[i] to plug into Lanczos' formula
    p = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    if (n < 0.5) {
        return Math.PI / Math.sin(n * Math.PI) / gamma(1 - n);
    } else {
        n--;
        var x = p[0];
        for (var i = 1; i < g + 2; i++) {
            x += p[i] / (n + i);
        }
        var t = n + g + 0.5;
        return Math.sqrt(2 * Math.PI) * Math.pow(t, (n + 0.5)) * Math.exp(-t) * x;
    }
}

function factorial(n) {
    if (n === 0) return 1;
    return n * factorial(n - 1);
}

function gammaPDF(x, alpha, beta) {
    if (x < 0 || alpha < 0 || beta < 0)
        return NaN;
    return ((Math.pow(beta, alpha)) / (gamma(alpha))) * Math.pow(x, alpha-1) * Math.exp(-beta*x);
}

function likelihoodPP(t, k, lambda) {
    return (Math.exp(-lambda * t) * Math.pow((lambda * t), k)) / factorial(k);
}

//infer the likeliest rate of a homogenous PP for all events
function inferPoissonHomogenous(allProcesses, t, priorAlpha, priorBeta) {
    if (t < 1 || priorAlpha < 0 || priorBeta < 0)
        return NaN;
    var events = sortEvents(allProcesses)[1],
        bestParam = 1,
        bestLikelihood = 0,
        k = events.length;
    console.log("k = " + k);
    for (var i = 0.001; i < 1; i += 0.001) {
        console.log("i = " + i);
        console.log("g " + gammaPDF(i, priorAlpha, priorBeta));
        console.log("l " + likelihoodPP(t, k, i));
        likelihood = gammaPDF(i, priorAlpha, priorBeta) * likelihoodPP(t, k, i);
        console.log(likelihood);
        if (likelihood > bestLikelihood) {
            bestLikelihood = likelihood;
            bestParam = i;
        }
    } return bestParam;
}

//best fit lambda for homogenous poisson process
function bestFitRateHPP(t, k, priorAlpha, priorBeta) {
    return (priorAlpha + k -1).toFixed(2) / (priorBeta + t).toFixed(2);
}

//poissonprocess(lambda) with k arrivals in t interval, gamma(a, b) prior
function posteriorProb(lambda, t, k, a, b) {
    return (Math.pow((b+t), (a+k)) / gamma(b+t)) * t * Math.pow(lambda, (a+k-1)) * Math.exp(-lambda * (b+t));
}

friendsHyp = [100, 100];
notFriendsHyp = [2, 2];

function friends(t, k) {
    lambda_0 = bestFitRateHPP(t, k, notFriendsHyp[0], notFriendsHyp[1]);
    lambda_1 = bestFitRateHPP(t, k, friendsHyp[0], friendsHyp[1]);
    console.log(lambda_0);
    console.log(lambda_1);
    p_h0 = posteriorProb(lambda_0, t, k, notFriendsHyp[0], notFriendsHyp[1]);
    p_h1 = posteriorProb(lambda_1, t, k, friendsHyp[0], friendsHyp[1]);
    console.log(p_h0);
    console.log(p_h1);
    return p_h1 > p_h0;
}

console.log(friends(100, 1));
console.log(friends(100, 1000));



