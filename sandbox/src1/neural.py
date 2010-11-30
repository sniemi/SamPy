from numpy import arange, newaxis, sin
from pylab import randn, plot, scatter, hold
from monte.arch.neuralnet import NeuralnetIsl
from monte.gym import trainer

mynn        = NeuralnetIsl(1,10,1)   #neural network with one input-, one output-,
                                     #and one hidden layer with 10 sigmoid units
mytrainer  = trainer.Conjugategradients(mynn,10)

inputs = arange(-10.0,10.0,0.1)[newaxis,:]        #produce some inputs
outputs = sin(inputs) + randn(1,inputs.shape[1])  #produce some outputs
testinputs  = arange(-10.5,10.5,0.05)[newaxis,:]  #produce some test-data
testoutputs = sin(testinputs)

for i in range(50):
    hold(False)
    scatter(inputs[0],outputs[0])
    hold(True)
    plot(testinputs[0],mynn.apply(testinputs)[0][0])
    mytrainer.step((inputs,outputs),0.0001)
    print mynn.cost((inputs,outputs),0.0001)
