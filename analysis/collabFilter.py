import collections
import cPickle as pickle
import os
import tools
import time

def addMissingSimilarSubreddits(neededSubreddits, similarSubredditDict, subredditVectors, savefilename, simType):
    for i, neededSubreddit in enumerate(neededSubreddits, 1):
        print "Processing {}: {}".format(i, neededSubreddit)
        if neededSubreddit in similarSubredditDict:
            print "Skipping: {}".format(neededSubreddit)
            continue
        queryVector = subredditVectors[neededSubreddit]
        similarSubredditPairs = tools.getMostSimilar(neededSubreddit, queryVector, subredditVectors, 100, simType)
        similarSubredditDict[neededSubreddit] = similarSubredditPairs
        if i % 200 == 0 or i == len(neededSubreddits):
            print "Checkpointing"
            with open(savefilename, 'w') as outfile:
                pickle.dump(similarSubredditDict, outfile)
    return similarSubredditDict

def collabFilterRecs(oldSubreddits, similarSubredditDict, simType, n=10, k=100):
    # TODO: This currently ignores simType
    recSubreddits = collections.defaultdict(int)
    for oldSubreddit in oldSubreddits:
        similarSubreddits = similarSubredditDict[oldSubreddit][:k]
        for score, similarSubreddit in similarSubreddits:
            recSubreddits[similarSubreddit] += score

    for oldSubreddit in oldSubreddits:
        if oldSubreddit in recSubreddits:
            del recSubreddits[oldSubreddit]

    recSubredditList = []
    for recSubreddit, score in recSubreddits.iteritems():
        recSubredditList.append((score, recSubreddit))
    recSubredditList.sort(reverse=True)
    return recSubredditList[:n]

if __name__ == "__main__":
    # Switch to desired similarity type.
    simType = "jaccard"

    # Load everything.
    print "Loading user id indexes"
    indexToUserId, userIdToIndex = tools.loadIndexToUserId("../bigData/collabFilter/indexToUserId")
    print "Loading subreddit vectors"
    subredditVectors = tools.loadSubredditVectors("../bigData/collabFilter/subredditVectors.pkl")
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = tools.getUserIdToSubredditsByType("../bigData/finalGeneration/devUsers", "oldSubreddits")
    print "Loading user id to new subreddits"
    userIdToNewSubreddits = tools.getUserIdToSubredditsByType("../bigData/finalGeneration/devUsers", "newSubreddits")
    print "Loading subreddit id to name"
    subredditIdToName = tools.read_subreddit_names("../bigData/subredditIdToName")

    # Extract needed subreddits.
    neededSubreddits = set()
    for userId, oldSubreddits in userIdToOldSubreddits.iteritems():
        for oldSubreddit in oldSubreddits:
            neededSubreddits.add(oldSubreddit)
    print "Need {} subreddits".format(len(neededSubreddits))

    # Filter out all not needed subredditVector < 10 users
    for subredditId in list(subredditVectors.keys()):
        if subredditId not in neededSubreddits and len(subredditVectors[subredditId]) < 10:
            del subredditVectors[subredditId]
    print "Total subreddits after filter: {}".format(len(subredditVectors))

    print "Loading similarity info"
    similarSubredditFilename = "../bigData/finalGeneration/{}Sims.pkl".format(simType)
    similarSubredditDict = {}
    if os.path.isfile(similarSubredditFilename):
        with open(similarSubredditFilename, 'r') as infile:
            similarSubredditDict = pickle.load(infile)
    else:
        print "Similarity info not found, starting from scratch"
    start = time.time()
    addMissingSimilarSubreddits(neededSubreddits, similarSubredditDict, subredditVectors, similarSubredditFilename, simType)

    # Get recs.
    precision10 = 0
    mrrMetric = 0
    mapMetric = 0
    numUsers = 0
    for i, (userId, oldSubreddits) in enumerate(userIdToOldSubreddits.iteritems()):
        print "--------------------------------------"
        recs = collabFilterRecs(oldSubreddits, similarSubredditDict, simType)
        print "Taken: {}".format(time.time() - start)

        # Precision at 10.
        goodRec10Count = 0
        for _, rec in recs[:10]:
            if rec in userIdToNewSubreddits[userId]:
                goodRec10Count += 1
        precision10 += goodRec10Count / 10.

        # Mean Reciprocal Rank.
        for rank, (_, rec) in enumerate(recs, 1):
            if rec in userIdToNewSubreddits[userId]:
                mrrMetric += 1. / rank
                break

        # Mean Average Precision.
        correctSoFar = 0
        numActual = float(len(userIdToNewSubreddits[userId]))
        for rank, (_, rec) in enumerate(recs, 1):
            if rec in userIdToNewSubreddits[userId]:
                correctSoFar += 1
                mapMetric += correctSoFar / numActual / rank

        # Print out.
        print "Processing {} {} {}".format(i, userId, goodRec10Count)
        print "--------------collab------------------"
        line = ""
        for rec in recs[:10]:
            line += " {} ".format(subredditIdToName[rec[1]])
        print line
        print "--------------------------------------"
        print ""

    totalUsers = float(len(userIdToOldSubreddits))
    print "precision@10: {}, mrr: {}, map: {}".format(
        precision10 / totalUsers,
        mrrMetric / totalUsers,
        mapMetric / totalUsers)
