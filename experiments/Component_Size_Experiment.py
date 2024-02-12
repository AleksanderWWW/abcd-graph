import matplotlib.pyplot as plt
import Hypergraph_Models as hm
import Hypergraph_Processes as hp
from Dataset_Reader import read_data as rd
import numpy as np

#You can replace with your own set of txt files or replace V and E manually
#Use Dataset_Reader.write_data to save a hypergraph as a file
filenames = {'hospital-lyon',
#             'NDC-substances',
#             'email-eu',
#             'tags-math-sx',
#             'tags-ask-ubuntu',
#             'email-enron',
#             'contact-primary-school',
#             'contact-high-school',
#             'diseasome',
#             'disgenenet'
            }

max_size = 5
num_rolls = 1

for filename in filenames:

    #Get V and E from the file
    V,E = rd(filename)

    #Run component_size_growth on the actual graph num_rolls times
    real_data = dict.fromkeys(list(range(num_rolls)))
    for i in real_data.keys():
        real_data[i] = hp.giant_component_growth(V,E)

    #Run the same thing on Chung-Lu resamples
    synthetic_data = dict.fromkeys(list(range(num_rolls)))
    for i in synthetic_data.keys():
        E_chung_lu = hm.chung_lu(V,E)
        synthetic_data[i] = hp.giant_component_growth(V,E_chung_lu)

    x = list(range(len(E)+1))
    #Getting average results for y axis
    y_real = [1]
    y_synthetic = [1]
    for m in range(1,len(E)+1):
        y_real.append(np.average([real_data[i][m] for i in real_data.keys()]))
        y_synthetic.append(np.average([synthetic_data[i][m] for i in synthetic_data.keys()]))

    cutoff = len(V)

    #Making plots
    plt.plot(x[0:cutoff],y_real[0:cutoff], label = 'Actual')
    plt.plot(x[0:cutoff],y_synthetic[0:cutoff], label = 'Simulation')
    plt.legend()
    plt.title('{0} giant component growth'.format(filename))
    #plt.savefig('{0}-growth.png'.format(filename))
    plt.show()
    plt.close()
        

