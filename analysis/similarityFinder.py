import argparse
import json
import tools

def loadSubredditVector(infilename, neededSubreddit):
    with open(infilename, 'r') as infile:
        for line in infile:
            lineJson = json.loads(line)
            subredditId = lineJson.keys()[0]
            if subredditId == neededSubreddit:
                return set(lineJson[subredditId])

def loadSubredditVectorsPart(infilename, start, end):
    """
    Outputs dictionary of subredditId -> set of userIdIndexes
    """
    subredditVectors = {}
    with open(infilename, 'r') as infile:
        for i, line in enumerate(infile):
            if i < start or i >= end:
                continue
            lineJson = json.loads(line)
            subredditId = lineJson.keys()[0]
            subredditVectors[subredditId] = set(lineJson[subredditId])
    return subredditVectors

def getMostSimilar(querySubredditId, queryVector, subredditVectors, k=10):
    similarities = []
    for i, (subredditId, subredditVector) in enumerate(subredditVectors.iteritems(), 1):
        similarity = tools.jaccardSim(queryVector, subredditVector)
        if subredditId == querySubredditId:
            continue
        similarities.append((similarity, subredditId))
        if i % 1000 == 0:
            print "Processed: {}".format(i)
    similarities.sort(reverse=True)
    return similarities[:k]

# Loads a 1/8 of the subredditVectors and finds similarity for those.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--divideNum", "-d", type=int, required=True)
    args = parser.parse_args()

    # Should be in tools but being sloppy due to time.
    print "Loading user id to old subreddits"
    userIdToOldSubreddits = {}
    neededSubreddits = set()
    with open("../bigData/analysis/oldSubredditsDev", 'r') as infile:
        for line in infile:
            lineJson = json.loads(line)
            userIdToOldSubreddits[lineJson["userId"]] = lineJson["oldSubreddits"]
            neededSubreddits.update(lineJson["oldSubreddits"])

    # Get part of subredditVectors
    divides = []
    for i in range(0, 9):
        divides.append(17986 * i)
    start = divides[args.divideNum]
    end = divides[args.divideNum+1]
    print "Loading: {} {}".format(start, end)
    subredditVectors = loadSubredditVectorsPart("../bigData/analysis/subredditVectors", start, end)
    print "Subreddits: {}".format(len(subredditVectors))

    # Iterate and calculate.
    for neededSubreddit in neededSubreddits:
        print "Processing: {}".format(neededSubreddit)
        queryVector = loadSubredditVector("../bigData/analysis/subredditVectors", neededSubreddit) 
        similarSubredditPairs = getMostSimilar(neededSubreddit, queryVector, subredditVectors, 50)
        similarSubreddits = [subreddit for _, subreddit in similarSubredditPairs]
        similarScores = [score for score, _ in similarSubredditPairs]
        with open("../bigData/analysis/similarSubreddits2/part" + str(args.divideNum), 'a') as outfile:
            subredditJson = {}
            subredditJson["subredditId"] = neededSubreddit
            subredditJson["similarSubreddits"] = similarSubreddits
            subredditJson["scores"] = similarScores
            outfile.write(json.dumps(subredditJson) + "\n")
