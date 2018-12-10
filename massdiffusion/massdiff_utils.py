import json
import numpy as np
from scipy import sparse

def parseDevSet(devfile):
    devSet = {}
    with open(devfile) as infile:
        for line in infile:
            parsed_json = json.loads(line)
            devSet[parsed_json['userId']] = {'oldSubreddits': [str(u) for u in parsed_json['oldSubreddits']], 'newSubreddits': [str(u) for u in sorted(parsed_json['newSubreddits'], key=parsed_json['newSubreddits'].get, reverse = True)], 'connectedUsers': []}
    return devSet

def createDictionaries(infile):
    print('creating dictionaries')
    users = set()
    subreddits = set()
    print('reading file')
    with open(infile) as inf:
        for line in inf:
            user, subreddit, _ = line.split(' ')
            users.add(user)
            subreddits.add(subreddit)

    users_to_id = {k: v for v, k in enumerate(list(users))}
    id_to_users = {v: k for v, k in enumerate(list(users))}
    subs_to_id = {k: v for v, k in enumerate(list(subreddits))}
    id_to_subs = {v: k for v, k in enumerate(list(subreddits))}
    print('done creating dictionaries')
    return users_to_id,subs_to_id,id_to_users,id_to_subs

def createDatastructures(infile, users_to_id, subs_to_id):
    subredditUser = {}
    A = sparse.dok_matrix((len(subs_to_id),len(users_to_id)),dtype=int)
    R = sparse.dok_matrix((len(subs_to_id),len(users_to_id)),dtype=int)
    print('creating data structures')
    i = 0
    with open(infile) as inf:
        for line in inf:
            user, subreddit, comments = line.split(' ')
            if i%100000 == 0:
                print(i)
            subredditId = subs_to_id[subreddit]
            userId = users_to_id[user]
            if subredditId not in subredditUser:
                subredditUser[subredditId] = set()
            subredditUser[subredditId].add(userId)
            A[subredditId,userId] = 1
            R[subredditId,userId] = int(comments)
            i +=1
    print('done creating A,R')
    print(i)
    return subredditUser, A, R

def createA(infile, users_to_id, subs_to_id):
    subredditUser = {}
    A = sparse.dok_matrix((len(subs_to_id),len(users_to_id)),dtype=int)
    print('creating A')
    i = 0
    with open(infile) as inf:
        for line in inf:
            user, subreddit, comments = line.split(' ')
            if i%100000 == 0:
                print(i//100000)
            subredditId = subs_to_id[subreddit]
            userId = users_to_id[user]
            if subredditId not in subredditUser:
                subredditUser[subredditId] = set()
            subredditUser[subredditId].add(userId)
            A[subredditId,userId] = 1
            i +=1
    print('done creating A')
    print(i)
    return subredditUser, sparse.csc_matrix(A)
 
def createR(infile, users_to_id, subs_to_id):
    R = sparse.dok_matrix((len(subs_to_id),len(users_to_id)),dtype=int)
    print('creating R')
    i = 0
    with open(infile) as inf:
        for line in inf:
            user, subreddit, comments = line.split(' ')
            if i%100000 == 0:
                print(i//100000)
            subredditId = subs_to_id[subreddit]
            userId = users_to_id[user]
            R[subredditId,userId] = int(comments)
            i +=1
    print('done creating R')
    print(i)

    return sparse.csc_matrix(R)