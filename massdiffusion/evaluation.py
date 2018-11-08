import json
from helperfunctions import user_to_index, index_to_user, subreddit_to_index, index_to_subreddit
from md_utils import getftilde


def createDevSet(fname,users_to_index, subreddits_to_index):
    devSet = {}
    with open(fname) as infile:
            for line in infile:
                parsed_json = json.loads(line)
                devSet[user_to_index(parsed_json['userId'])] =  [subreddit_to_index(str(y)) for y in x.keys() for x in parsed_json['newSubreddits']]
                print devSet[user_to_index(parsed_json['userId'])]
    return devSet


def evaluateDevSet(devSet,W_H,A):
    for k in devSet.keys():
        ftilde = getftilde(W_H,A,k)
        sorted_index = sorted(range(len(ftilde)), key=ftilde.__getitem__,reverse=True)[:len(devSet[k])]
        predicted_subreddit = [index_to_subreddit[x] for x in sorted_index]
        print predicted_subreddit
        