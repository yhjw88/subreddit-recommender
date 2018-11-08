import collections
import cPickle as pickle
import json

if __name__ == "__main__":
    correctSubreddits = ["t5_2z7qd", "t5_2z166", "t5_2qh03", "t5_2qh1e", "t5_2tex6"]


    similarSubreddits = collections.defaultdict(dict)
    infilePrefix = "../bigData/analysis/similarSubreddits/part"
    for i in range(8):
        infilename = infilePrefix + str(i)
        print "Loading: {}".format(infilename)
        with open(infilename, 'r') as infile:
            for j, line in enumerate(infile):
                subredditJson = json.loads(line)
                subreddit = correctSubreddits[j]
                # subreddit = subredditJson["subredditId"]
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
    with open("../bigData/analysis/similarSubreddits/full.pkl", 'w') as outfile:
        pickle.dump(similarSubredditDump, outfile)
