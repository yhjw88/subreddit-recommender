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
    precision10 = 0
    mrrMetric = 0
    mapMetric = 0
    numUsers = 0
    for i, (userId, oldSubreddits) in enumerate(userIdToOldSubreddits.iteritems()):
        print "--------------------------------------"
        recs = []
        for _, subredditId in subredditsByPop:
            if subredditId in oldSubreddits:
                continue
            recs.append(subredditId)

        # Precision at 10.
        goodRec10Count = 0
        for rec in recs[:10]:
            if rec in userIdToNewSubreddits[userId]:
                goodRec10Count += 1
        precision10 += goodRec10Count / 10.

        # Mean Reciprocal Rank.
        for rank, rec in enumerate(recs, 1):
            if rec in userIdToNewSubreddits[userId]:
                mrrMetric += 1. / rank
                break

        # Mean Average Precision.
        correctSoFar = 0
        numActual = float(len(userIdToNewSubreddits[userId]))
        for rank, rec in enumerate(recs, 1):
            if rec in userIdToNewSubreddits[userId]:
                correctSoFar += 1
                mapMetric += correctSoFar / numActual / rank

        # Print out.
        print "Processing {} {} {}".format(i, userId, goodRec10Count)
        print "----------------old-------------------"
        line = ""
        for oldSubreddit in oldSubreddits:
            line += " {} ".format(subredditIdToName[oldSubreddit])
        print line

        print "----------------new-------------------"
        correctAnswers = userIdToNewSubreddits[userId]
        line = ""
        for answer in correctAnswers:
            line += " {} ".format(subredditIdToName[answer])
        print line
        print "----------------pop-------------------"
        line = ""
        for rec in recs[:10]:
            line += " {} ".format(subredditIdToName[rec])
        print line
        print "--------------------------------------"
        print ""

    totalUsers = float(len(userIdToOldSubreddits))
    print "precision@10: {}, mrr: {}, map: {}".format(
        precision10 / totalUsers,
        mrrMetric / totalUsers,
        mapMetric / totalUsers)
