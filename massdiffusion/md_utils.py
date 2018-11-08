import numpy as np
from scipy import sparse
from helperfunctions import user_to_index, index_to_user, subreddit_to_index, index_to_subreddit


''''
****************************************************************************
function to parse in text file and create dictionaries of users and subreddits to corresponding IDS
text file format is (user, subreddit, number of comments)
****************************************************************************
'''

def createDictionaries(inputfname,outputfname, filter):
    users = set()
    subreddits = set()
    print 'reading file'   
    print 'writing output file'
    outfile = open(outputfname, 'wb')
    with open(inputfname) as infile:
        for line in infile:
            user, subreddit, comments = line.split(' ')
            if int(comments) > filter:
                users.add(user)
                subreddits.add(subreddit)
                outfile.write(line)
    outfile.close()
    users_to_index = {k: v for v, k in enumerate(list(users))}
    subreddits_to_index = {k: v for v, k in enumerate(list(subreddits))}
    print 'done reading file'
    return users_to_index,subreddits_to_index


'''
****************************************************************************
function to parse in text file and create sparse adjacency matrix A
text file format is (user, subreddit, number of comments)
sparse adjacency matrix is DOK format, A[i,j] is 1 when user j comments on subreddit i
****************************************************************************
'''


def createA(fname, users_to_index, subreddits_to_index):
    print 'creating A'
    A = sparse.dok_matrix((len(subreddits_to_index),len(users_to_index)),dtype=int)
    print 'still creating A'
    with open(fname) as infile:
        i = 0
        for line in infile:
            print i
            user, subreddit, comments = line.split(' ')
            userID = user_to_index(users_to_index,user)
            subredditID = subreddit_to_index(subreddits_to_index,subreddit)
            A[subredditID,userID] = 1
            i +=1
    print 'done creating A'
    return A

''''
****************************************************************************
function to create transition matrix W given adjacency matrix A
****************************************************************************


def createW(A):
    ko = A.sum(axis=1, dtype = 'float')  
    ku = A.sum(axis = 0, dtype = 'float').T 
    W_H =  A*(A.T/ku)/ko
    return W_H
'''


def createW(A):
    print 'creating ko'
    ko = A.sum(axis=1, dtype = 'float')
    print 'creating ku'  
    ku = A.sum(axis = 0, dtype = 'float').T
    print 'creating W'
    noOfSubreddits = A.shape[0]
    noOfUsers = A.shape[1]
    W_H = sparse.dok_matrix((noOfSubreddits,noOfSubreddits),dtype=float)
    for a in range(noOfSubreddits):
        print 'a %d' %a
        for b in range(noOfSubreddits):
            for j in range(noOfUsers):
                W_H[a,b] += A[a,j]*A[b,j]/ku[j] 
            W_H[a,b] = W_H[a,b]/ko[a]
    print 'done creating W'
    return W_H


def getftilde(W_H,A,i):
    print 'getting f'
    f_i = A[:,i]    
    ftilde_i = np.dot(W_H,f_i.todense()).T
    print 'done getting f'
    return ftilde_i.tolist()[0]

'''

def getftilde(W_H,A,i):
    f_i = A[:,i]    
    ftilde_i = np.dot(W_H,f_i.todense())
    return ftilde_i


def createW(A, i):
ko = A.sum(axis=1, dtype = 'float',keepdims = True)  
ku = A.sum(axis = 0, dtype = 'float', keepdims = True).T 
W_H =  np.matmul(A,(A.T/ku))/ko

    return W_H

def getftilde(W_H,A,i):
f_i = A[:,i]    
ftilde_i = np.dot(W_H,f_i)

'''