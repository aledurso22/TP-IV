#%%
#let's try to observe the double descent phenomenon
import torch
import numpy as np
import torchvision
import matplotlib.pyplot as plt
import torch.nn as nn

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(torch.cuda.get_device_name(device))
#check if it's the right gpu
print(device)

random_seed = 1
torch.manual_seed(random_seed)


class one_hidden(nn.Module):
    def __init__(self,d, H):
        super().__init__()
        
        self.layers = nn.Sequential(
      nn.Linear(d, H, bias = False),
      nn.ReLU(),
      nn.Linear(H, 1, bias = False)
    )
        self.d = d
        self.H = H
        self.flatten = nn.Flatten()

    def forward(self, x):
        x = self.flatten(x)
        x = self.layers(x / self.d**0.5)
        return x.reshape((len(x),)) / self.H

batch_size_train = 4096
batch_size_test = 12288


train_loader = torch.utils.data.DataLoader(
  torchvision.datasets.MNIST('/files/', train=True, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor()
                             ])),
  batch_size=batch_size_train, shuffle=True)

test_loader = torch.utils.data.DataLoader(
  torchvision.datasets.MNIST('/files/', train=False, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor()
                             ])),
  batch_size=batch_size_test, shuffle=True)

first_batch_train = enumerate(train_loader)


batch_idx, (X_train, y_train) = next(first_batch_train)
d = X_train.shape[-1]
print(X_train.shape)
X_train = X_train.to(device)
y_train = y_train.to(device)


first_batch_test = enumerate(test_loader)
batch_idx_test, (X_test, y_test) = next(first_batch_test)
print(X_test.shape)
X_test = X_test.to(device)
y_test = y_test.to(device)

L_th = 0.085
dL_th = 1e-3
maxsteps = 700000 
ps = np.array([1, 2, 4, 5, 6, 8, 9])
L_trains = []
L_tests = []

#here add the p and print the different
for p in ps:
  numbers_parameters= p*(d**2 + 1)
  print(f'numbers of parameters ={numbers_parameters}')
  student = one_hidden(d*d, p)
  student.to(device)
  optimizer = torch.optim.SGD(student.parameters(), lr=1)

  #I inizialize some variables:
  delta_L = 1
  L_train = 1
  i = 0
  if p == 2:
    L_th = 0.045
  if p == 4:
    L_th = 0.015



  
  while (L_train>L_th or delta_L > dL_th) and i<maxsteps:
  

    y_train_label = y_train%2 #1 if odd and 0 if even



    y_pred_train = student(X_train)
    L_train =(1/batch_size_train) * ( (y_train_label - y_pred_train ) ** 2).sum()  
    optimizer.zero_grad()
    L_train.backward()
    optimizer.step() 
    y_pred_train = student(X_train)
    L_train_new = (1/batch_size_train) * ( (y_train_label - y_pred_train ) ** 2).sum()

    delta_L = abs(L_train - L_train_new)
    if i % 1000 == 0: print(f'step {i} - L_train={L_train.item()}')
    i += 1


  counter = 0

  with torch.no_grad():
    y_test_label = y_test%2 #1 if odd and 0 if even
    y_pred_test = student(X_test)
    L_test =(1/batch_size_test) * ( (y_test_label - y_pred_test ) ** 2).sum()
    print(f'L_test={L_test.item()}')
 
  L_train = L_train.to("cpu")
  L_test = L_test.to("cpu")
  L_trains.append(L_train.detach())
  L_tests.append(L_test.detach())



plt.plot( ( (ps * ((d**2) + 1) )/batch_size_train ), np.array(L_trains),'-ok')

plt.xlabel('n_param/n_train')
plt.ylabel('L train')
plt.yscale('log')
plt.xscale('log')
plt.show()

plt.plot( ( (ps * ((d**2) + 1) )/batch_size_train ), np.array(L_tests),'-ok')

plt.xlabel('n_param/n_train')
plt.ylabel('L test')
plt.yscale('log')
plt.xscale('log')
plt.show()

#%%
#now let's study the learning rate      
import torch
import numpy as np
import torchvision
import matplotlib.pyplot as plt
import torch.nn as nn
from scipy.optimize import curve_fit

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(torch.cuda.get_device_name(device))
#check if it's the right gpu
print(device)

random_seed = 1
torch.manual_seed(random_seed)



class one_hidden(nn.Module):
    def __init__(self,d, H):
        super().__init__()
        
        self.layers = nn.Sequential(
      nn.Linear(d, H, bias = False),
      nn.ReLU(),
      nn.Linear(H, 1, bias = False)
    )
        self.d = d
        self.H = H
        self.flatten = nn.Flatten()

    def forward(self, x):
        x = self.flatten(x)
        x = self.layers(x / self.d**0.5)
        return x.reshape((len(x),)) / self.H

batch_size_test = 12288

batch_size_train = 8192







train_loader = torch.utils.data.DataLoader(
  torchvision.datasets.MNIST('/files/', train=True, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor()
                             ])),
  batch_size=batch_size_train, shuffle=True)

test_loader = torch.utils.data.DataLoader(
  torchvision.datasets.MNIST('/files/', train=False, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor()
                             ])),
  batch_size=batch_size_test, shuffle=True)

first_batch_train = enumerate(train_loader)
#here low the size



first_batch_test = enumerate(test_loader)
batch_idx_test, (X_test, y_test) = next(first_batch_test)
print(X_test.shape)
X_test = X_test.to(device)
y_test = y_test.to(device)

batch_idx, (X_train, y_train) = next(first_batch_train)
d = X_train.shape[-1]

L_th = 0.015
dL_th = 1e-3 
maxsteps = 100000
p = 8
numbers_parameters= p*(d**2 + 1)
print(f'numbers of parameters ={numbers_parameters}')

L_trains = []
L_tests = []
mses = []

n_s = np.array([1024, 2048, 4096, 8192])
for n_ in n_s:
    X_train_cut = X_train[:n_][:][:][:]
    y_train_cut = y_train[:n_]
    print(X_train_cut.shape)
    X_train_cut = X_train_cut.to(device)
    y_train_cut = y_train_cut.to(device)





    student = one_hidden(d*d, p)
    student.to(device)
    optimizer = torch.optim.SGD(student.parameters(), lr=1)
    

  
    delta_L = 1
    L_train = 1
    i = 0




    
    while (L_train>L_th or delta_L > dL_th) and i<maxsteps:
    

      y_train_label = y_train_cut%2 #1 if odd and 0 if even



      y_pred_train = student(X_train_cut)
      L_train =(1/n_) * ( (y_train_label - y_pred_train ) ** 2).sum()  
      optimizer.zero_grad()
      L_train.backward()
      optimizer.step() 
      y_pred_train = student(X_train_cut)
      L_train_new = (1/n_) * ( (y_train_label - y_pred_train ) ** 2).sum()

      delta_L = abs(L_train - L_train_new)
      if i % 1000 == 0: print(f'step {i} - L_train={L_train.item()}')
      i += 1


    with torch.no_grad():
      y_test_label = y_test%2 #1 if odd and 0 if even
      y_pred_test = student(X_test)
      L_test =(1/batch_size_test) * ( (y_test_label - y_pred_test ) ** 2).sum()
      print(f'L_test={L_test.item()}')
  

    L_train = L_train.to("cpu")
    L_test = L_test.to("cpu")
    L_trains.append(L_train.detach())
    L_tests.append(L_test.detach())


def objective(x, A, beta):
 return A * x**(beta)
popt, _ = curve_fit(objective, n_s, np.array(L_tests))
A, beta = popt
y_fit = objective(n_s, A, beta)

print(f"A = {A}")
print(f"beta = {beta}")

plt.plot( n_s, np.array(L_tests),'-ok', label = 'Error test')
plt.plot(n_s , y_fit, label = 'fitting')
plt.xlabel('number of train size')
plt.ylabel('L test')
plt.yscale('log')
plt.xscale('log')
plt.legend()
plt.show()





