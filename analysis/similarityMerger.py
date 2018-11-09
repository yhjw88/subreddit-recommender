import collections
import cPickle as pickle
import json

if __name__ == "__main__":
    similarSubreddits = collections.defaultdict(dict)
    infilePrefix = "../bigData/analysis/similarSubreddits2/part"
    for i in range(8):
        infilename = infilePrefix + str(i)
        print "Loading: {}".format(infilename)
        with open(infilename, 'r') as infile:
            for j, line in enumerate(infile):
                subredditJson = json.loads(line)
                subreddit = subredditJson["subredditId"]
                for similarSubreddit, score in zip(subredditJson["similarSubreddits"], subredditJson["scores"]):
                    similarSubreddits[subreddit][similarSubreddit] = (score, similarSubreddit)

    print "Dumping"
    similarSubredditDump = {}
    for subreddit, similars in similarSubreddits.iteritems():
        similarSubredditList = [] 
        for _, pair in similars.iteritems():
            similarSubredditList.append(pair)
        similarSubredditList.sort(reverse=True)
        similarSubredditDump[subreddit] = similarSubredditList
    with open("../bigData/analysis/similarSubreddits2/full.pkl", 'w') as outfile:
        pickle.dump(similarSubredditDump, outfile)
