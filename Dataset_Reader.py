#Create a new text file for a given hypergraph

#V: vertices
#E: edges
#filename: The file name you want

def write_data(V,E,filename):
    f = open('datasets\{0}.txt'.format(filename),'w')
    f.write('nodes\n')
    for v in V:
        f.write('{0}\n'.format(v))
    f.write('edges\n')
    
    if type(E[0]) is list:
        E = [['{0}'.format(str(v)) for v in e] for e in E]
    else:
        E = [{'{0}'.format(str(v)) for v in e} for e in E]

    for e in E:
        f.write('{0}\n'.format(e))
    f.close()
        

#Get vertices and edges from a text file

#filename: the name of the file, without .txt

def read_data(filename):
    f = open('datasets\{0}.txt'.format(filename),'r')
    file = f.read().splitlines()
    f.close()

    V = set()
    E = []
    Vstart = file.index('nodes')
    Estart = file.index('edges')
    end = len(file)
    for i in range(Vstart+1,Estart):
        V.add(file[i])
    for i in range(Estart+1,end):
        if (len(eval(file[i]))<=5):
            E.append(eval(file[i]))

    return V,E
