import collections
import cPickle as pickle
import tools

def addMissingSimilarSubreddits(neededSubreddits, similarSubredditDict, subredditVectors, savefilename, simType):
    for i, neededSubreddit in enumerate(neededSubreddits, 1):
        print "Processing {}: {}".format(i, neededSubreddit)
        if neededSubreddit in similarSubredditDict:
            print "Skipping: {}".format(neededSubreddit)
            continue
        queryVector = subredditVectors[neededSubreddit]
        similarSubredditPairs = tools.getMostSimilar(neededSubreddit, queryVector, subredditVectors, 100, simType)
        similarSubredditDict[neededSubreddit] = similarSubredditPairs
        if i % 50 == 0 or i == len(neededSubreddits):
            print "Checkpointing"
            with open(savefilename, 'w') as outfile:
                pickle.dump(similarSubredditDict, outfile)
    return similarSubredditDict

def collabFilterRecs(oldSubreddits, similarSubredditDict, simType, n=2, k=20):
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
    simType = "cosine"

    # Load everything.
    print "Loading user id indexes"
    indexToUserId, userIdToIndex = tools.loadIndexToUserId("../bigData/collabFilter/indexToUserId")
    print "Loading subreddit vectors"
    subredditVectors = tools.loadSubredditVectors("../bigData/collabFilter/subredditVectors.pkl")
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = tools.getUserIdToSubredditsByType("../bigData/devTest/devUsers", "oldSubreddits")
    print "Loading user id to new subreddits"
    userIdToNewSubreddits = tools.getUserIdToSubredditsByType("../bigData/devTest/devUsers", "newSubreddits")
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
    similarSubredditFilename = "../bigData/collabFilter/{}Sims.pkl".format(simType)
    similarSubredditDict = {}
    # with open(similarSubredditFilename, 'r') as infile:
    #     similarSubredditDict = pickle.load(infile)
    addMissingSimilarSubreddits(neededSubreddits, similarSubredditDict, subredditVectors, similarSubredditFilename, simType)

    # Do collab filtering
    numGood = 0
    numTotal = 0
    for userId, oldSubreddits in userIdToOldSubreddits.iteritems():
        recs = collabFilterRecs(oldSubreddits, similarSubredditDict, simType)

        goodRecs = []
        badRecs = []
        for _, rec in recs:
            if rec in userIdToNewSubreddits[userId]:
                goodRecs.append(subredditIdToName[rec])
            else:
                badRecs.append(subredditIdToName[rec])
        numGood += len(goodRecs)
        numTotal += len(goodRecs) + len(badRecs)

        # print "Predicted: {}".format(recs)
        # print "Actual: {}".format(userIdToNewSubreddits["IndigoForever900"])

        # print "Old: {}".format([subredditIdToName[thing] for thing in userIdToOldSubreddits[userId]])
        # print "New: {}".format([subredditIdToName[thing] for thing in actuals])
        # print "Good: {}".format(goodRecs)
        # print "Bad: {}".format(badRecs)
    print "Precision @10: {}".format(numGood / float(numTotal))



    # # print subredditVectors["t5_3b749"]
    # # print subredditVectors["t5_2s427"]
    # # print getMostSimilar(subredditVectors["t5_3b749"], subredditVectors)
    # # Do collab filtering.
    # # for userId, newSubreddits in userIdToNewSubreddits.iteritems():
    # #     oldSubreddits = userIdToOldSubreddits[userId]
