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

def getUserIdToSubredditsByType(infilename, subredditType):
    """
    Loads subreddits from the given file of the given subredditType.
    Legal options are "newSubreddits" and "oldSubreddits"
    Output is dictionary of userId -> subreddits
    subreddits is dictionary of subredditId -> count
    """
    userIdToSubreddits = {}
    with open(infilename, 'r') as infile:
        for i, line in enumerate(infile, 1):
            lineJson = json.loads(line)
            userIdToSubreddits[lineJson["userId"]] = lineJson["newSubreddits"]
            if i % 1000000 == 0:
                print "Processed {}".format(i)
    return userIdToSubreddits

def loadIndexToUserId(infilename):
    """
    Outputs indexToUserId, userIdToIndex
    """
    indexToUserId = []
    userIdToIndex = {}
    with open(infilename, 'r') as infile:
        for line in infile:
            userId = line.strip()
            userIdToIndex[userId] = len(indexToUserId)
            indexToUserId.append(userId)
    return indexToUserId, userIdToIndex

def loadSubredditVectors(infilename):
    """
    Outputs dictionary of subredditId -> set of userIdIndexes
    """
    subredditVectors = {}
    with open(infilename, 'r') as infile:
        for line in infile:
            lineJson = json.loads(line)
            subredditId = lineJson.keys()[0]
            subredditVectors[subredditId] = set(lineJson[subredditId])
    return subredditVectors

def jaccardSim(subreddits1, subreddits2):
    num1 = len(subreddits1)
    num2 = len(subreddits2)

    numIntersect = 0
    if num1 < num2:
        for subreddit in subreddits1:
            if subreddit in subreddits2:
                numIntersect += 1
    else:
        for subreddit in subreddits2:
            if subreddit in subreddits1:
                numIntersect += 1
    numUnion = num1 + num2 - numIntersect

    return numIntersect / float(numUnion)

def getMostSimilar(querySubredditId, queryVector, subredditVectors, k=10):
    similarities = []
    for i, (subredditId, subredditVector) in enumerate(subredditVectors.iteritems(), 1):
        similarity = jaccardSim(queryVector, subredditVector)
        if subredditId == querySubredditId:
            continue
        similarities.append((similarity, subredditId))
        if i % 10000 == 0:
            print "Processed: {}".format(i)
    similarities.sort(reverse=True)
    return similarities[:k]
