function hawkesProcess (baseRate, maxRate, name) {
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
			for (var j = 0; j < process.events.length; j++) { 
				rate += this.decay(theta, t, process.events[j]);
			}
		} return Math.min(rate, this.maxRate);
	}

	this.excitedBy = function(otherHP, decayFunct, theta) {
		this.excitors.push([otherHP, decayFunct, theta]);
	}

	/*theta - decay parameter
	  t - current time
	  s - event to excite */
	this.decay = function(theta, t, s) {
		return Math.exp(-theta * (t - s))
	}

}

function simulate(allProcesses, ticksPerHour) {
	var t = 0;
	var numEvents = 0;
	var process;
	maxTime = 3600 * 24 * 7;
	maxEvents = 1000;
	while (t < maxTime && numEvents < maxEvents) {
		for (var p = 0; p < allProcesses.length; p++) {
			process = allProcesses[p];
			if (Math.random() < (process.currentRate(t) / ticksPerHour)) {
				process.events.push(t);
				numEvents++;
				break;
			}
		}
        t++;
	}

}


