# Tools for graph analysis
import json

def read_subreddit_names(filename):
    """
    Reads in file with global mappings from subreddit ids to names.
    Filters out subreddit names that begin with 'u_'.

    Examples: [subreddit_id subreddit_name]
        ...
        t5_3m6wn hormuz
        t5_bx9mz u_Ubiver
        ...

    Returns a dictionary mapping from id to name and a set of
    unique subreddit ids.
    """
    subreddit_name_dict = {} # id -> subreddit
    with open(filename) as f:
        for line in f:
            subreddit_id, subreddit_name = line.split()
            if subreddit_name.startswith('u_'): # not subreddit!
                continue
            subreddit_name_dict[subreddit_id] = subreddit_name
    return subreddit_name_dict

def readUserIdFilters(infilename, userIdsToFilter):
    with open(infilename, 'r') as f:
        for i, line in enumerate(f, 1):
            userIdsToFilter.add(line.strip())
    return userIdsToFilter

def getUserIdToSubreddits(infilename, userIdToSubreddits, subredditIdToName=None, userIdsToFilter=set(), includeCounts=False):
    print "Processing {}".format(infilename)
    with open(infilename, 'r') as f:
        for i, line in enumerate(f, 1):
            userId, subredditId, commentCount = line.split()
            if subredditIdToName is not None and subredditId not in subredditIdToName:
                continue
            if userId in userIdsToFilter:
                continue
            if includeCounts:
                userIdToSubreddits[userId][subredditId] += int(commentCount)
            else:
                userIdToSubreddits[userId].add(subredditId)

            if i % 1000000 == 0:
                print "Processed {}".format(i)
    return userIdToSubreddits

def loadNewSubreddits(infilename):
    """
    Output is dictionary of userId -> newSubreddits
    newSubreddits is dicionary of subredditId -> count
    """
    userIdToNewSubreddits = {}
    with open(infilename, 'r') as infile:
        for i, line in enumerate(infile, 1):
            lineJson = json.loads(line)
            userIdToNewSubreddits[lineJson["userId"]] = lineJson["newSubreddits"]
            if i % 1000000 == 0:
                print "Processed {}".format(i)
    return userIdToNewSubreddits






