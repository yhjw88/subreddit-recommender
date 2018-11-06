import json
import collections
import sys

def generateUserSubreddit(infilename, outfilename):
    userSubreddit = collections.defaultdict(int)
    with open(infilename, 'r') as infile:
        for i, line in enumerate(infile, 1):
            parsedLine = json.loads(line)
            user = parsedLine["author"]
            subreddit = parsedLine["subreddit_id"]
            if user == "[deleted]":
                continue

            userSubreddit[(user, subreddit)] += 1
            if i % 100000 == 0:
                print "Processed {}".format(i)

    with open(outfilename, 'w') as outfile:
        for (user, subreddit), count in userSubreddit.iteritems():
            outfile.write("{} {} {}\n".format(user, subreddit, count))


if __name__ == "__main__":
    infilename = "bigData/raw/RC_2018-01"
    outfilename = "bigData/userSubreddit/RC_2018-01"
    generateUserSubreddit(infilename, outfilename)
