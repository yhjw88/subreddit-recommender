import collections
import cPickle as pickle
import json
import tools

def addMissingSimilarSubreddits(neededSubreddits, similarSubredditDict, subredditVectors, savefilename):
    for i, neededSubreddit in enumerate(neededSubreddits):
        print "Processing {}: {}".format(i, neededSubreddit)
        if neededSubreddit in similarSubredditDict:
            print "Skipping: {}".format(neededSubreddit)
            continue
        queryVector = subredditVectors[neededSubreddit]
        similarSubredditPairs = tools.getMostSimilar(neededSubreddit, queryVector, subredditVectors, 100)
        similarSubredditDict[neededSubreddit] = similarSubredditPairs
        with open("../bigData/analysis/similarSubreddits3/full.pkl", 'w') as outfile:
            pickle.dump(similarSubredditDict, outfile)
    return similarSubredditDict

def collabFilterRecs(oldSubreddits, similarSubredditDict, n=2, k=20):
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
    # Load everything.
    print "Loading user id indexes"
    indexToUserId, userIdToIndex = tools.loadIndexToUserId("../bigData/analysis/indexToUserId")
    print "Loading subreddit vectors"
    subredditVectors = tools.loadSubredditVectors("../bigData/analysis/subredditVectors")
    print "Loading user id to new subreddits"
    userIdToNewSubreddits = tools.loadNewSubreddits("../bigData/analysis/actualNewSubredditsDev")
    print "Loading subreddit id to name"
    subredditIdToName = tools.read_subreddit_names("../bigData/subredditIdToName")

    # Should be in tools but being sloppy due to time.
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = {}
    neededSubreddits = set()
    with open("../bigData/analysis/oldSubredditsDev", 'r') as infile:
        for i, line in enumerate(infile):
            lineJson = json.loads(line)
            userIdToOldSubreddits[lineJson["userId"]] = lineJson["oldSubreddits"]
            neededSubreddits.update(lineJson["oldSubreddits"])
    print "Need {} subreddits".format(len(neededSubreddits))

    # Filter out all not needed subredditVector < 10 users
    for subredditId in list(subredditVectors.keys()):
        if subredditId not in neededSubreddits and len(subredditVectors[subredditId]) < 10:
            del subredditVectors[subredditId]
    print "Total subreddits after filter: {}".format(len(subredditVectors))

    # print "Loading similarity info"
    similarSubredditFilename = "../bigData/analysis/similarSubreddits3/full.pkl"
    similarSubredditDict = {}
    with open(similarSubredditFilename, 'r') as infile:
        similarSubredditDict = pickle.load(infile)
    addMissingSimilarSubreddits(neededSubreddits, similarSubredditDict, subredditVectors, similarSubredditFilename)

    # Do collab filtering
    numGood = 0
    numTotal = 0
    for userId, oldSubreddits in userIdToOldSubreddits.iteritems():
        recs = collabFilterRecs(oldSubreddits, similarSubredditDict)
        actuals = []
        for rec in userIdToNewSubreddits[userId]:
            thing = rec.keys()[0]
            actuals.append(thing)

        goodRecs = []
        badRecs = []
        for _, rec in recs:
            if rec in actuals:
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
