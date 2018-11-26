# Tools for graph analysis
import cPickle as pickle
import json
import math

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
            userIdToSubreddits[lineJson["userId"]] = lineJson[subredditType]
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
    Outputs dictionary of subredditId -> dict mapping integer userIndex to count
    """
    if infilename.endswith("json"):
        return loadSubredditVectorsJson(infilename)
    if infilename.endswith("pkl"):
        return loadSubredditVectorsPkl(infilename)

def loadSubredditVectorsJson(infilename):
    subredditVectors = {}
    with open(infilename, 'r') as infile:
        for line in infile:
            lineJson = json.loads(line)
            subredditId = lineJson.keys()[0]
            subredditVectors[subredditId] = {}
            for userIndex, count in lineJson[subredditId].iteritems():
                subredditVectors[subredditId][int(userIndex)] = count
    return subredditVectors

def loadSubredditVectorsPkl(infilename):
    subredditVectors = None
    with open(infilename, 'r') as infile:
        subredditVectors = pickle.load(infile)
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

def getL2Norm(vector):
    vectorSum = 0
    for _, value in vector.iteritems():
        vectorSum += value**2
    return math.sqrt(vectorSum)

def cosineSim(subredditId1, subredditId2, subredditVectors, l2NormCache):
    subreddits1 = subredditVectors[subredditId1]
    subreddits2 = subredditVectors[subredditId2]
    if subredditId1 not in l2NormCache:
        l2NormCache[subredditId1] = getL2Norm(subreddits1)
    if subredditId2 not in l2NormCache:
        l2NormCache[subredditId2] = getL2Norm(subreddits2)
    denom = l2NormCache[subredditId1] * l2NormCache[subredditId2]

    num1 = len(subreddits1)
    num2 = len(subreddits2)
    numer = 0
    if num1 < num2:
        for subreddit, count in subreddits1.iteritems():
            if subreddit in subreddits2:
                numer += count * subreddits2[subreddit]
    else:
        for subreddit, count in subreddits2.iteritems():
            if subreddit in subreddits1:
                numer += count * subreddits1[subreddit]

    return numer / float(denom)

def getMostSimilar(querySubredditId, queryVector, subredditVectors, k=10, simType="jaccard"):
    cache = {}
    similarities = []
    for i, (subredditId, subredditVector) in enumerate(subredditVectors.iteritems(), 1):
        if simType == "jaccard":
            similarity = jaccardSim(queryVector, subredditVector)
        elif simType == "cosine":
            similarity = cosineSim(querySubredditId, subredditId, subredditVectors, cache)
        else:
            raise Exception("{} not acceptable as a simType".format(simType))
        if subredditId == querySubredditId:
            continue
        similarities.append((similarity, subredditId))
        if i % 10000 == 0:
            print "Processed: {}".format(i)
    similarities.sort(reverse=True)
    return similarities[:k]
