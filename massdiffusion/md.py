from md_utils import createDictionaries, createA, createW, getftilde
from evaluation import createDevSet, evaluateDevSet
from scipy import sparse
import numpy as np



'''
**************************************
Main function to create adjacency matrix, run mass diffusion and get results
**************************************
'''

def main():
    fname = 'inputGraph.txt'
    filtered = 'filtered.txt'
    devfname = 'actualNewSubredditsDev.txt'
    filter = 25
    users_to_index,subreddits_to_index = createDictionaries(fname, filtered, filter)

    A = createA(filtered, users_to_index, subreddits_to_index)
    print 'A shape'
    print A.shape

    #outfile = open('saveA.p','wb')
    #pickle.dump(A,outfile, protocol = 2)
    #outfile.close()
    #print 'A is pickled'

    #infile = open('saveA.p','rb')
    #A = pickle.load(infile)
    #infile.close()

    W_H = createW(A)
    print 'W_H shape'
    print W_H.shape
    print 'W is pickled'

    #outfile = open('saveW.p','wb')
    #pickle.dump(W_H,outfile,protocol = 2)
    #outfile.close()
    #print 'W is pickled'

    #infile = open('saveW','rb')
    #W_H = pickle.load(infile)
    #infile.close()
    
    devSet = createDevSet(devfname,users_to_index, subreddits_to_index)
    evaluateDevSet(devSet,W_H,A)










    





main()