import collections
import cPickle as pickle
import numpy as np
import tools

# Makes things at least 25x faster :)
class RandomBuffer:
    def __init__(self, N, alpha):
        self.index = 0
        self.buffer = []
        self.bufferSize = 2 * N
        self.distIndex = 0
        self.distBuffer = []
        self.distBufferSize = int(N * alpha / 10.)
        self.alpha = alpha

    def getNext(self):
        self.index += 1
        if self.index >= len(self.buffer):
            self.index = 0
            self.buffer = np.random.random((self.bufferSize,))
        return self.buffer[self.index]
    
    # TODO: We're drawing from the geometric distribution for each walk here.
    # The Pixie paper does not mention the distribution, but this has precedence in PageRank.
    # This also means alpha will be the mean length of walks, node2vec uses 80-100.
    def getNextDist(self):
        self.distIndex += 1
        if self.distIndex >= len(self.distBuffer):
            self.distIndex = 0
            self.distBuffer = np.random.geometric(p=self.alpha, size=self.distBufferSize)
            # self.distBuffer = np.full((self.distBufferSize,), int(1. / self.alpha))
        return self.distBuffer[self.distIndex]

def getMaxSubredditDegree(subredditIndexToUsers):
    maxOldSubredditDegree = 0
    for subredditIndex, users in enumerate(subredditIndexToUsers):
        if len(users) > maxOldSubredditDegree:
            maxOldSubredditDegree = len(users)
    return maxOldSubredditDegree 

def doRandomWalks(subredditIndex,
                  userIndexToSubreddits,
                  subredditIndexToUsers,
                  N,
                  randomBuffer):
    subredditIndexToScoreUpdates = collections.defaultdict(float)
    totalSteps = 0
    while totalSteps < N:
        currentSubreddit = subredditIndex
        currentUser = None
        currentMaxSteps = randomBuffer.getNextDist()
        for i in range(currentMaxSteps):
            # Next user.
            # Unweighted.
            rand1 = int(len(subredditIndexToUsers[currentSubreddit]) * randomBuffer.getNext())
            currentUser = subredditIndexToUsers[currentSubreddit][rand1]
            # Weighted.
            # randNum = randomBuffer.getNext()
            # accumulated = 0
            # for weight, userIndex in subredditIndexToUsers[currentSubreddit]:
            #     accumulated += weight
            #     if accumulated >= randNum:
            #         currentUser = userIndex
            #         break

            # Next subreddit.
            # Unweighted.
            rand2 = int(len(userIndexToSubreddits[currentUser]) * randomBuffer.getNext())
            currentSubreddit = userIndexToSubreddits[currentUser][rand2]
            # Weighted.
            # randNum = randomBuffer.getNext()
            # accumulated = 0
            # for weight, subredditIndex in userIndexToSubreddits[currentSubreddit]:
            #     accumulated += weight
            #     if accumulated >= randNum:
            #         currentSubreddit = subredditIndex
            #         break

            # Record.
            subredditIndexToScoreUpdates[currentSubreddit] += 1
        totalSteps += currentMaxSteps
    return subredditIndexToScoreUpdates

def getRecs(oldSubreddits,
            subredditIdToIndex,
            indexToSubredditId,
            userIndexToSubreddits,
            subredditIndexToUsers,
            N=50000,
            n=10,
            alpha=0.5):
    randomBuffer = RandomBuffer(N, alpha)
    maxSubredditDegree = getMaxSubredditDegree(subredditIndexToUsers)
    oldSubredditIndexList = [subredditIdToIndex[oldSubredditId] for oldSubredditId in oldSubreddits]

    # Normalize the weights.
    weights = [oldSubreddits[indexToSubredditId[oldSubredditIndex]] for oldSubredditIndex in oldSubredditIndexList]
    weights = np.array(weights)
    weights = weights / float(np.sum(weights))

    # Calculate scaling factors.
    scalingFactors = []
    for oldSubredditIndex, weight in zip(oldSubredditIndexList, weights):
        oldSubredditDegree = len(subredditIndexToUsers[oldSubredditIndex])
        # if oldSubredditDegree == 0:
        #     scalingFactors.append(0)
        #     continue
        scalingFactors.append(oldSubredditDegree * (maxSubredditDegree - np.log(oldSubredditDegree)))
    sumScalingFactors = np.sum(scalingFactors)

    # TODO: Incorporate some sort of weighting on the number of steps here.
    subredditIndexToScore = collections.defaultdict(float)
    totalSteps = 0
    for i, (oldSubredditIndex, scalingFactor, weight) in enumerate(zip(oldSubredditIndexList, scalingFactors, weights)):
        # numSteps = N * (scalingFactor / float(sumScalingFactors))
        numSteps = N / float(len(scalingFactors)) 
        totalSteps += numSteps
        # print "num: {} numSteps: {} totalSteps: {}, elapsed: {}".format(i, numSteps, totalSteps, (time.time() - start) / 60.)
        subredditIndexToScoreUpdates = doRandomWalks(oldSubredditIndex,
                                                     userIndexToSubreddits,
                                                     subredditIndexToUsers,
                                                     numSteps,
                                                     randomBuffer)
        for subredditIndex, score in subredditIndexToScoreUpdates.iteritems():
            subredditIndexToScore[subredditIndex] += np.sqrt(score)

    # TODO: Squaring doesn't affect the ranks.
    recSubredditList = []
    for subredditIndex, score in subredditIndexToScore.iteritems():
        recSubreddit = indexToSubredditId[subredditIndex]
        if recSubreddit in oldSubreddits:
            continue
        recSubredditList.append((score, recSubreddit))
    recSubredditList.sort(reverse=True)

    if n is not None:
        return recSubredditList[:n]
    return recSubredditList

if __name__ == "__main__":
    # Load everything.
    print "Loading user id indexes"
    indexToUserId, userIdToIndex = tools.loadIndexToUserId("../bigData/pixie/indexToUserId")
    print "Loading subreddit id indexes"
    indexToSubredditId, subredditIdToIndex = tools.loadIndexToUserId("../bigData/pixie/indexToSubredditId")
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = tools.getUserIdToSubredditsByType("../bigData/finalGeneration/expUsers", "oldSubreddits")
    print "Loading user id to new subreddits"
    userIdToNewSubreddits = tools.getUserIdToSubredditsByType("../bigData/finalGeneration/expUsers", "newSubreddits")
    print "Loading subreddit id to name"
    subredditIdToName = tools.read_subreddit_names("../bigData/subredditIdToName")
    print "Loading user index to subreddits"
    userIndexToSubreddits = None
    with open("../bigData/pixie/userIndexToSubreddits.pkl", 'r') as infile:
        userIndexToSubreddits = pickle.load(infile)
    print "Loading subreddit index to user"
    subredditIndexToUsers = None
    with open("../bigData/pixie/subredditIndexToUsers.pkl", 'r') as infile:
        subredditIndexToUsers = pickle.load(infile)

    # Get recs.
    numGood = 0
    numTotal = 0
    for i, (userId, oldSubreddits) in enumerate(userIdToOldSubreddits.iteritems()):
        print "Processing {}".format(i)
        recs = getRecs(oldSubreddits,
                       subredditIdToIndex,
                       indexToSubredditId,
                       userIndexToSubreddits,
                       subredditIndexToUsers)


        goodRecs = []
        badRecs = []
        for _, rec in recs:
            if rec in userIdToNewSubreddits[userId]:
                goodRecs.append(subredditIdToName[rec])
            else:
                badRecs.append(subredditIdToName[rec])
        numGood += len(goodRecs)
        numTotal += len(goodRecs) + len(badRecs)

        if i >= 0:
            break

        # print "Predicted: {}".format(recs)
        # print "Actual: {}".format(userIdToNewSubreddits["IndigoForever900"])

        # print "Old: {}".format([subredditIdToName[thing] for thing in userIdToOldSubreddits[userId]])
        # print "New: {}".format([subredditIdToName[thing] for thing in actuals])
        # print "Good: {}".format(goodRecs)
        # print "Bad: {}".format(badRecs)
    print "Total Recs: {}".format(numTotal)
    print "Precision @10: {}".format(numGood / float(numTotal))
