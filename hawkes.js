function hawkesProcess (baseRate, maxRate) {
	this.baseRate = baseRate;
	this.events = [];
	this.excitors = [];
	this.maxRate = maxRate;

	this.currentRate = function(t) {
		rate = this.baseRate;
		for (var i = 0; i < this.excitors.length; i++) { 
			process = this.excitors[i][0];
			theta = this.excitors[i][2];
			for (var j = 0; j < this.process.events.length; j++) { 
				rate += decay(theta, t, process.events[j]);
			}
		} return Math.min(rate, this.maxRate);
	}

	this.excitedBy = function(otherHP, decayFunct, theta) {
		this.excitors.append([otherHP, decayFunct, theta]);
	}

	this.nextEvent = function(start) {
		while (true) {
			 
		}
	}


	
	/*theta - decay parameter
	  t - current time
	  s - event to excite */
	this.decay = function(theta, t, s) {
		return Math.exp(-theta * (t - s))
	}

}

f = new hawkesProcess(.5, 10);
g = new hawkesProcess(1, 10);
f.excitedBy(g, f.decay, 1);
console.log(f.baseRate);
console.log(f.currentRate(5));
