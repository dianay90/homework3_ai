#!/usr/bin/env python
# coding: utf-8

import numpy as np ## For numerical python
import pandas as pd
import time
import os
from tqdm import trange
import matplotlib.pyplot as plt
from IPython.display import clear_output


class DNN():
    def __init__(self, sizes, epochs=110, l_rate=0.003):
        self.sizes = sizes
        self.epochs = epochs
        self.l_rate = l_rate

        # we save all parameters in the neural network in this dictionary
        self.params = self.initialization()
        print('')


    def __init__2(self,  epochs,l_rate):
        self.epochs = epochs
        self.l_rate = l_rate

        self.params = {
            'W1':np.random.randn(128, 784) * np.sqrt(1. / 128),
            'W2':np.random.randn(64, 128) * np.sqrt(1. / 64),
            'W3':np.random.randn(10, 64) * np.sqrt(1. / 10)
        }



    def sigmoid(self, x, derivative=False):
        if derivative:
            return (np.exp(-x))/((np.exp(-x)+1)**2)
        return 1/(1 + np.exp(-x))
    
    #two version
    def sigmoid2(self, x):
    
        return 1/(1 + np.exp(-x))
    
    def sigmoid_with_derivative(self, x):
    
        return (np.exp(-x))/((np.exp(-x)+1)**2)
    

    def softmax(self, x, derivative=False):
        # Numerically stable with large exponentials
        exps = np.exp(x - x.max())
        if derivative:
            return exps / np.sum(exps, axis=0) * (1 - exps / np.sum(exps, axis=0))
        return exps / np.sum(exps, axis=0)

    def softmax2(self, x):

        #the x is an array and you subtract x.max from each item in the array 
        exps = np.exp(x - x.max())     
        return exps / np.sum(exps, axis=0)        

    def softmax_with_derivative2(self,x):
        exps = np.exp(x - x.max())
        return exps / np.sum(exps, axis=0) * (1 - exps / np.sum(exps, axis=0))

    def initialization(self):
        # number of nodes in each layer
        input_layer=self.sizes[0]
        hidden_1=self.sizes[1]
        hidden_2=self.sizes[2]
        output_layer=self.sizes[3]

        params = {
            'W1':np.random.randn(hidden_1, input_layer) * np.sqrt(1. / hidden_1),
            'W2':np.random.randn(hidden_2, hidden_1) * np.sqrt(1. / hidden_2),
            'W3':np.random.randn(output_layer, hidden_2) * np.sqrt(1. / output_layer)
        }

        return params

    def forward_pass(self, x_train):
        params = self.params

        # input layer activations becomes sample
        params['A0'] = x_train

        # input layer to hidden layer 1
        params['Z1'] = np.dot(params["W1"], params['A0'])
        params['A1'] = self.sigmoid(params['Z1'])

        # hidden layer 1 to hidden layer 2
        params['Z2'] = np.dot(params["W2"], params['A1'])
        params['A2'] = self.sigmoid(params['Z2'])

        # hidden layer 2 to output layer
        params['Z3'] = np.dot(params["W3"], params['A2'])
        params['A3'] = self.softmax(params['Z3'])

        return params['A3']

    def forward_matrix_multiply(self, variableI, variableII):
        finalParam = variableI.dot(variableII)
        return finalParam 
        
    def forward_propagation(self, x_array):
        #for loop or major function call out
        parameter_values = self.params

        # multiple weights by prevoius layer activation, then apply act function
        parameter_values['A0'] = x_array

        # matrix multipliy input to first hidden layer, then apply activation function
        parameter_values['Z1'] = self.forward_matrix_multiply(parameter_values['W1'], parameter_values['A0'])
        parameter_values['A1'] = self.sigmoid(parameter_values['Z1'])

        # matrix multiply input to first hidden layer, then apply activation function

        parameter_values['Z2'] = self.forward_matrix_multiply(parameter_values['W2'], parameter_values['A1'])
        parameter_values['A2'] = self.sigmoid(parameter_values['Z2'])

        # matrix multiple hidden layer two to output layer, then apply softmax since it's the last year
        parameter_values['Z3'] = self.forward_matrix_multiply(parameter_values['W3'], parameter_values['A2'])
        parameter_values['A3'] = self.softmax(parameter_values['Z3'])

        return parameter_values['A3']

    def predict(self, x_val):

        predictions = []

        for x in x_val:
            output = self.forward_pass(x)
            predictions.append(np.argmax(output))
        
        return predictions
    def predict2(self, x_val):

        predictions = list()

        for x in x_val:
            output = self.forward_pass(x)
            predictions.append(np.argmax(output))
        
        return predictions

    def backward_pass(self, y_train, output):
       #dot,name
        params = self.params
        change_w = {}

        # Calculate W3 update
        error = 2 * (output - y_train) / output.shape[0] * self.softmax(params['Z3'], derivative=True)
        change_w['W3'] = np.outer(error, params['A2'])
        # Calculate W2 update
        error = np.dot(params['W3'].T, error) * self.sigmoid(params['Z2'], derivative=True)
        change_w['W2'] = np.outer(error, params['A1'])

        # Calculate W1 update
        error = np.dot(params['W2'].T, error) * self.sigmoid(params['Z1'], derivative=True)
        change_w['W1'] = np.outer(error, params['A0'])

        return change_w
    
    def product_of_vectors(self, error, param): 
        product = np.matrix(error).T.dot(np.matrix(param))
        #np.matrix(error).T.dot(np.matrix(params['A2']))
        return product

    def backward_propogation(self, updated_output):
     # test this 
        parameter_values = self.params
        updated_weights = list()

        error = self.softmax_with_derivative2(parameter_values['Z3']) * updated_output * 2
        updated_weights['W3'] = np.matrix(error).T.dot(np.matrix(parameter_values['A2']))


        # Calculate W2 update
        error =  self.sigmoid_with_derivative(parameter_values['Z2']) *parameter_values['W3'].T.dot(error) 
        updated_weights['W2'] = np.matrix(error).T.dot(np.matrix(parameter_values['A1']))


        # Calculate W1 update
        error =  self.sigmoid_with_derivative(parameter_values['Z1']) * parameter_values['W2'].T.dot(error)
        updated_weights['W1'] = np.matrix(error).T.dot(np.matrix(parameter_values['A0']))

        return updated_weights

    def update_network_parameters(self, changes_to_w):
 
        
        for key, value in changes_to_w.items():
            self.params[key] -= self.l_rate * value

    def compute_accuracy(self, x_val, y_val):

        predictions = []

        for x, y in zip(x_val, y_val):
            output = self.forward_pass(x)
            pred = np.argmax(output)
            predictions.append(pred == np.argmax(y))
        
        return np.mean(predictions)

    def compute_accuracy2(self, x_val, y_val):

        predictions = list()

        for x, y in zip(x_val, y_val):
            output = self.forward_pass(x)
            pred = np.argmax(output)
            predictions.append(pred == np.argmax(y))
        
        return np.mean(predictions)

    def train(self, x_train, y_train, x_val, y_val):

        train_log,val_log = [], []
        start_time = time.time()
        for iteration in range(self.epochs):
            for x,y in zip(x_train, y_train):
                output = self.forward_pass(x)
                changes_to_w = self.backward_pass(y, output)
                self.update_network_parameters(changes_to_w)
            
            train_log.append(self.compute_accuracy(x_train, y_train))
            val_log.append(self.compute_accuracy(x_val, y_val))
    
            clear_output()
            print("Train accuracy:",train_log[-1])
            print("Val accuracy:",val_log[-1])
            plt.plot(train_log,label='train accuracy')
            plt.plot(val_log,label='val accuracy')
            plt.legend(loc='best')
            plt.grid()
            plt.show()


            accuracy = self.compute_accuracy(x_val, y_val)
            print('Epoch: {0}, Time Spent: {1:.2f}s, Accuracy: {2:.2f}%'.format(
                iteration+1, time.time() - start_time, accuracy * 100
            ))


    def train2(self, x_train, y_train, x_val, y_val):

        train_log,val_log = [], []
        start_time = time.time()
        for iteration in range(self.epochs):
            for x,y in zip(x_train, y_train):
                output = self.forward_pass(x)
                update_output = (output- y)/output.shape[0]
                changes_to_w = self.backward_pass(update_output)
                self.update_network_parameters(changes_to_w)
            
            train_log.append(self.compute_accuracy(x_train, y_train))
            val_log.append(self.compute_accuracy(x_val, y_val))
    
            clear_output()
            print("Train accuracy:",train_log[-1])
            print("Val accuracy:",val_log[-1])
            plt.plot(train_log,label='train accuracy')
            plt.plot(val_log,label='val accuracy')
            plt.legend(loc='best')
            plt.grid()
            plt.show()


            accuracy = self.compute_accuracy(x_val, y_val)
            print('Epoch: {0}, Time Spent: {1:.2f}s, Accuracy: {2:.2f}%'.format(
                iteration+1, time.time() - start_time, accuracy * 100
            ))


def load_dataset():
    import pandas as pd
    Xtest=pd.read_csv("/home/dianayoh/homework3/homework3_ai/test_image.csv",header=None)
    ytest=pd.read_csv("/home/dianayoh/homework3/homework3_ai/test_label.csv",header=None)
    Xtrain=pd.read_csv("/home/dianayoh/homework3/homework3_ai/train_image.csv",header=None)
    ytrain=pd.read_csv("/home/dianayoh/homework3/homework3_ai/train_label.csv",header=None)
    X_train=np.array(Xtrain)[:].reshape((-1, 28, 28))

    X_test=np.array(Xtest)[:].reshape((-1, 28, 28))

    X_test = (X_test/255).astype('float32')
    X_train = (X_train/255).astype('float32')
    y_train=np.array(ytrain[0])
    y_test=np.array(ytest[0])
  
    arrtr= np.random.randint(0,60000,10000)   #randomly select the 10000 images from training.csv
    arrte= np.random.randint(0,60000,10000)   #randomly select the 10000 images from training.csv
     
    X_train, X_val = X_train[arrtr], X_train[arrte]
    y_train, y_val = y_train[arrtr], y_train[arrte]

    X_val = X_train
    y_val = y_train
 
    X_train = X_train.reshape([X_train.shape[0], -1])
    X_val = X_val.reshape([X_val.shape[0], -1])
    X_test = X_test.reshape([X_test.shape[0], -1])
    return X_train, y_train, X_val, y_val, X_test, y_test
    
X_train, y_train, X_val, y_val, X_test, y_test = load_dataset()



y_train = list(y_train)
y_val = list(y_val)
y_test = list(y_test)


y_train_temp, y_val_temp, y_test_temp =  [], [], []

for i in y_train:
  li = [0]*10
  li[i] = 1
  y_train_temp.append(li)


for i in y_val:
  li = [0]*10
  li[i] = 1
  y_val_temp.append(li)

for i in y_test:
  li = [0]*10
  li[i] = 1
  y_test_temp.append(li)


y_train = np.array(y_train_temp)
y_val = np.array(y_val_temp)
y_test = np.array(y_test_temp)


dnn = DNN(sizes=[784, 128, 64, 10])
'''

epoch = 110
l_rate = .003
dnn2 = DNN(epoch,l_rate)
'''
dnn.train(X_train, y_train, X_val, y_val)


pred = dnn.predict(X_test)
dataframe=pd.DataFrame(pd.Series(pred))
dataframe.to_csv(os.getcwd() + "test_predictions.csv", index=False)



