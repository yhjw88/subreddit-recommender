import cPickle as pickle
import tools

if __name__ == "__main__":
    # Load everything.
    print "Loading subreddit id indexes"
    indexToSubredditId, _ = tools.loadIndexToUserId("../bigData/pixie/indexToSubredditId")
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = tools.getUserIdToSubredditsByType("../bigData/finalGeneration/devUsers", "oldSubreddits")
    print "Loading user id to new subreddits"
    userIdToNewSubreddits = tools.getUserIdToSubredditsByType("../bigData/finalGeneration/devUsers", "newSubreddits")
    print "Loading subreddit id to name"
    subredditIdToName = tools.read_subreddit_names("../bigData/subredditIdToName")
    print "Loading subreddit index to user"
    subredditIndexToUsers = None
    with open("../bigData/pixie/subredditIndexToUsers.pkl", 'r') as infile:
        subredditIndexToUsers = pickle.load(infile)

    # Rank by most popular in # of users commenting.
    subredditsByPop = []
    for subredditIndex, users in enumerate(subredditIndexToUsers):
        subredditsByPop.append((len(users), indexToSubredditId[subredditIndex]))
    subredditsByPop.sort(reverse=True)

    # Get recs.
    numGood = 0
    numTotal = 0
    for i, (userId, oldSubreddits) in enumerate(userIdToOldSubreddits.iteritems()):
        recs = []
        for _, subredditId in subredditsByPop:
            if subredditId in oldSubreddits:
                continue
            recs.append(subredditId)
            if len(recs) == 10:
                break

        goodRecs = []
        badRecs = []
        for rec in recs:
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
    print "Total Recs: {}".format(numTotal)
    print "Precision @10: {}".format(numGood / float(numTotal))
