import matplotlib.pyplot as plt
import Hypergraph_Models as hm
import Hypergraph_Processes as hp
import numpy as np


num_vertices = 1000
num_edges = np.array([200,500,200,100,50,20])
weight_function = np.array([1/num_vertices]*num_vertices)
beta_values = [i/10 for i in range(11)]
num_rolls = 20
V = set(range(num_vertices))

for beta in beta_values:

    #Run the experiment num_roll times
    data = dict.fromkeys(list(range(num_rolls)))
    for i in data.keys():
        E = hm.Soft_CL(num_vertices,num_edges,weight_function,beta)
        data[i] = hp.giant_component_growth(V,E)

    x = list(range(len(E)+1))
    #Getting average results for y axis
    y = [1]
    for m in range(1,len(E)+1):
        y.append(np.average([data[i][m] for i in data.keys()]))

    #Adding plot for each beta
    plt.plot(x,y, label = 'Beta = {0}'.format(beta))

plt.xlabel('Number of edges added')
plt.ylabel('Size of largest component')

plt.legend()
plt.title('Giant component growth for various beta')
plt.show()
#plt.savefig('various-beta-growth.png')
plt.close()
        

