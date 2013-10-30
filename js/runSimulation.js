//rate is arrivals per hour

var eventIndex = 0;
var simulationSlowDown = .2; //higher number means a slower simulation
var start;
var simulation;

function runSimulation() {
    nameVector = ["Finn", "Jake", "Ice King"];

    friendMatrixTheta = [
        [0, .1, 0],
        [.1, 0, 0],
        [0, 0, 0]
                        ];

    friendMatrixBeta = [
        [0, 10000, 0],
        [10000, 0, 0],
        [0, 0, 0]
                       ];

    simulation = new simulateConversations(nameVector, friendMatrixTheta, friendMatrixBeta, simulationSlowDown, 3600);
    console.log(simulation.processes);
    //console.log(simulation.sortedEventsLabeled);
    //display on html
    for (var i = 0; i < simulation.sortedEventsLabeled.length; i++) {
        start = new Date();
        delay = simulation.sortedEventsLabeled[i][0];
        setTimeout(function() {
            $('#data tr:first').after('<tr><td>' + simulation.sortedEventsLabeled[eventIndex][1].split("to").toString() + '</td><td>' + simulation.sortedEventsLabeled[eventIndex][0] + '</td></tr>');
            eventIndex++;
        }, delay * simulation.slowdown);

    }
}

function reverseName(name) {
    return name.split('to').reverse().join('to');
}

function simulateConversations(nameVector, friendMatrixTheta, friendMatrixBeta, slowdown, ticksPerHour) {
    this.slowdown = slowdown;
    this.friendMatrixTheta = friendMatrixTheta;
    this.friendMatrixBeta = friendMatrixBeta;
    this.numPeople = nameVector.length;
    this.nameVector = nameVector;
    this.processes = []
    this.nameToProcessMap = {};

    //create processes
    var p;
    for (var i = 0; i < nameVector.length; i++) {
        for (var j = 0; j < nameVector.length; j++) {
            if (i === j) continue;
            this.processes.push(new hawkesProcess(.2, (100), nameVector[i] + "to" + nameVector[j]));
            p = this.processes[this.processes.length-1];
            this.nameToProcessMap[p.name] = p;
        }
    }
    
    //console.log(this.processes);
    //set excitation params
    for (var i = 0; i < nameVector.length; i++) {
        for (var j = 0; j < nameVector.length; j++) {
            if (i === j) continue;
            if (this.friendMatrixTheta[i][j] == 0) continue;
            from = nameVector[i];
            to = nameVector[j];

            excited = this.nameToProcessMap[from + "to" + to];
            excitor = this.nameToProcessMap[to + "to" + from];

            excited.excitedBy(excitor, excited.decay, this.friendMatrixTheta[i][j], this.friendMatrixBeta[i][j]);
        }
    }

   
    simulate(this.processes, ticksPerHour);

    var temp = sortEvents(this.processes);
    this.sortedEventsLabeled = temp[1],
    this.sortedEvents = temp[0];
}
