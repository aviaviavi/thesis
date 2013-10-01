from random import *

#should weights affect the maximum rate increase, or the decay or increase from one firing?

class NeuralNet(object):
	"""
	int - layer sizes
	float, int - time interval represents size of one time step in time time units. (0, 1]
	"""
	time = 0.0

	def __init__(self, layer_sizes, time_interval):
		self.inputs = []
		self.outputs = []
		self.hidden = []
		self.time_interval = time_interval
	def train(self, inputs, outputs):
		pass
	def compute(self, inputs):
		pass

	"helper functions, no need for user calls to these"
	def create_input_layer(self, size):
		if self.inputs:
			print 'this network already has inputs'
		else:
			for i in range(size):
				new_n = InputNeuron(self)
				self.inputs.append(new_n)
	def connect_layers(self, l1, l2):
		for x in l1:
			for y in l2:
				x.connect_forward(y)
	def create_hidden_layer(self, size):
		layer = []
		for i in range(size):
			new_n = HiddenUnit(self)
			layer.append(new_n)
		return layer
	def create_output_layer(self, size):
		if self.outputs:
			print 'this network already has outputs'
		else:
			for i in range(size):
				new_n = OutputNeuron(self)
				self.outputs.append(new_n)
	def present_stimulus(self, inputs):
		for i in range(len(inputs)):
			self.inputs[i].rate = inputs[i]

class Neuron(object):

	def __init__(self, network):
		self.times_fired = []
		self.network = network
		self.recovering = False
	def step(self):
		abstract
	def fire(self):
		abstract
	def rate(self):
		abstract

class InputNeuron(Neuron):

	def __init__(self, network):
		super(InputNeuron, self).__init__(network)
		self.rate = 0.001
		self.post_syn = []
	def step(self):
		if random() < (self.rate * self.network.time_interval):
			self.fire(self.network.time)
	def connect_forward(self, neuron):
		self.post_syn.append(neuron)
		neuron.connect_back(self)
	def fire(self):
		self.times_fired.append(self.network.time)
		for neuron in self.post_syn:
			# update rates for all neurons in post
			pass
	

class OutputNeuron(Neuron):

	def __init__(self, network):
		super(OutputNeuron, self).__init__(network)
		self.pre_syn = []
		self.weights = {}
	def fire(self, t):
		self.times_fired.append(t)
	def connect_back(self, neuron):
		#may want to inialize to one number?, -5 to 5? 0 to 1?
		self.weights[neuron] = randrange(0.0, 5.0)
		self.pre_syn.append(neuron)
	def step(self):
		pass

class HiddenUnit(Neuron):

	def __init__(self, network):
		super(HiddenUnit, self).__init__(network)
		self.pre_syn = []
		self.post_syn = []
		self.weights = {}
	def fire(self, t):
		self.times_fired.append(t)
	def connect_forward(self, neuron):
		self.post_syn.append(neuron)
		neuron.connect_back(self)
	def connect_back(self, neuron):
		#only called by connect forward
		self.weights[neuron] = randrange(0.0, 5.0)
		self.pre_syn.append(neuron)
	def fire(self, t):
		pass
	def step(self):
		pass