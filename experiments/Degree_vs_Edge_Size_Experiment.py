import numpy as np
import matplotlib.pyplot as plt
import Hypergraph_Functions as hf
from Dataset_Reader import read_data as rd

#You can replace this with your own files, or get V and E in a different way
#Read the README if you want to add your own txt file
filenames = {'hospital-lyon',
             'NDC-substances',
             'email-eu',
             'tags-math-sx',
             'tags-ask-ubuntu',
             'email-enron',
             'contact-primary-school',
             'contact-high-school',
             'diseasome',
             'disgenenet'
            }

#Set edge-size cutoff here
max_size = 100

for filename in filenames:

    #Get V and E from the data
    V,E = rd(filename)

    edge_sets = hf.edge_sets(V,E)
    degrees = {v : len(edge_sets[v]) for v in V}
    edge_sizes = {d : [] for d in set(degrees.values())}
    for v in V:
        if degrees[v] > 0:
            edge_sizes[degrees[v]].extend([len(e) for e in edge_sets[v]])
  
    #################
    ######PLOTS######
    #################

    d_list = sorted(edge_sizes.keys())
    x = []
    y = []
    for d in d_list:
        x.append(d)
        if len(edge_sizes[d]) > 0:
            y.append(sum(edge_sizes[d])/len(edge_sizes[d]))
        else:
            y.append(0)

    plt.plot(x, y, 'o')
    plt.plot(x, np.poly1d(np.polyfit(x, y, 1))(x))
    plt.xlabel('degree')
    plt.ylabel('average edge size')
    plt.title('{0}'.format(filename))

    #Comment/uncomment depending on what you want
    ######
    #plt.savefig('{0}-deg-vs-edge-size.png'.format(filename))
    plt.show()
    ######
    
    plt.close()

