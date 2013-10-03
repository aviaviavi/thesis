var eventIndex = 0;

function runSimulation() {
    console.log("here1");
    var f = new hawkesProcess(5, 100, 'f');
    var g = new hawkesProcess(5, 100, 'g');
    var h = new hawkesProcess(5, 100, 'h');
    f.excitedBy(g, f.decay, .001);
    g.excitedBy(f, g.decay, .001); 

    var processes = [f, g, h];
    simulate(processes, 3600);

    var sortedEvents = [];

    for (var i = 0; i < processes.length; i++) {
        var p = processes[i];
        for (var j = 0; j < p.events.length; j++) {
            sortedEvents.push([p.events[j], p.name]);
        }
    }

    sortedEvents.sort(function(a, b) {return a[0] - b[0];}); 

    for (var i = 0; i < sortedEvents.length; i++) {
        delay = sortedEvents[i][0];
        setTimeout(function() {
            $('#data tr:first').after('<tr><td>' + sortedEvents[eventIndex][1] + '</td><td>' + sortedEvents[eventIndex][0] + '</td></tr>');
            eventIndex++;
        }, delay);

    }

    console.log(sortedEvents);
}
