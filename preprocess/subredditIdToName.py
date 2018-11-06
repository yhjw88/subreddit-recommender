import json
import sys

def addToIdToName(infilename, idToName):
    print "Processing {}".format(infilename)
    with open(infilename, 'r') as infile:
        for i, line in enumerate(infile, 1):
            parsedLine = json.loads(line)
            subreddit = parsedLine["subreddit_id"]
            subredditName = parsedLine["subreddit"]
            idToName[subreddit] = subredditName

            if i % 100000 == 0:
                print "Processed {}".format(i)

if __name__ == "__main__":
    idToName = {}
    for i in range(1, 7):
        infilename = "../bigData/raw/RC_2018-0" + str(i)
        addToIdToName(infilename, idToName)

    outfilename = "../bigData/subredditIdToName"
    with open(outfilename, 'w') as outfile:
        for subreddit, subredditName in idToName.iteritems():
            outfile.write("{} {}\n".format(subreddit, subredditName))
