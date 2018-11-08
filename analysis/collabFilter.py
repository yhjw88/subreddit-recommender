import collections
import cPickle as pickle
import json
import tools

def collabFilterRecs(oldSubreddits, similarSubredditDict, n=10, k=20):
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
    # print "Loading user id indexes"
    # indexToUserId, userIdToIndex = tools.loadIndexToUserId("../bigData/analysis/indexToUserId")
    # print "Loading subreddit vectors"
    # subredditVectors = tools.loadSubredditVectors("../bigData/analysis/subredditVectors")
    print "Loading user id to new subreddits"
    userIdToNewSubreddits = tools.loadNewSubreddits("../bigData/analysis/actualNewSubredditsDev")

    # Should be in tools but being sloppy due to time.
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = {}
    with open("../bigData/analysis/oldSubredditsDev", 'r') as infile:
        for line in infile:
            lineJson = json.loads(line)
            userIdToOldSubreddits[lineJson["userId"]] = lineJson["oldSubreddits"]

    print "Loading similarity info"
    with open("../bigData/analysis/similarSubreddits/full.pkl", 'r') as infile:
        similarSubredditDict = pickle.load(infile)

    recs = collabFilterRecs(userIdToOldSubreddits["IndigoForever900"], similarSubredditDict)
    actuals = []
    for rec in userIdToNewSubreddits["IndigoForever900"]:
        thing = rec.keys()[0]
        actuals.append(thing)


    subredditIdToName = tools.read_subreddit_names("../bigData/subredditIdToName")

    # print "Predicted: {}".format(recs)
    # print "Actual: {}".format(userIdToNewSubreddits["IndigoForever900"])

    print "Old: {}".format([subredditIdToName[thing] for thing in userIdToOldSubreddits["IndigoForever900"]])
    print "New: {}".format([subredditIdToName[thing] for thing in actuals])
    for _, rec in recs:
        if rec in actuals:
            print subredditIdToName[rec]
        else:
            print "Not {}".format(subredditIdToName[rec])


    # print subredditVectors["t5_3b749"]
    # print subredditVectors["t5_2s427"]
    # print getMostSimilar(subredditVectors["t5_3b749"], subredditVectors)
    # Do collab filtering.
    # for userId, newSubreddits in userIdToNewSubreddits.iteritems():
    #     oldSubreddits = userIdToOldSubreddits[userId]
