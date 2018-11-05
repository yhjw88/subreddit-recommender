import sys, os
from collections import defaultdict

##############################################
# Data Constants
##############################################
comment_dir = 'data/comments/'
subreddit_id_file = 'data/subredditIdToName'

##############################################
# Utility Functions
##############################################
def base36decode(number):
    return int(number, 36)

##############################################
# Process Raw Reddit Data Functions
##############################################
def read_subreddit_ids(filename):
    """
    Reads in a mapping from subreddit ids to names. Reads
    the filename line by line. Filters out subreddit names
    that begin with 'u_'.

    Examples: [subreddit_id subreddit_name]
        t5_3m6wn hormuz
        t5_bx9mz u_Ubiver

    Returns a dictionary mapping from id to name and a set of
    unique subreddit ids.
    """
    subreddit_names = {} # id -> subreddit
    subreddit_ids = set() # unique ids
    with open(filename) as f:
        for line in f:
            id, subreddit = line.split()
            if subreddit.startswith('u_'): # not subreddit!
                continue
            subreddit_names[id] = subreddit
            subreddit_ids.add(id)
    return subreddit_names, subreddit_ids

def read_subreddit_comments(dirname, subreddit_ids):
    """
    Reads in files containing user-subreddit commenting counts. Each file
    name is of the format RC_YYYY-MM where YYYY and MM are year and month,
    respectively.

    Examples: [user subreddit_id comment_count]
        PGHContrarian68 t5_2ve45 4
        TheIncompetenceOfMan t5_2qh33 11

    Each edge is represented as (user, subreddit_id) and is weighted by
    the cumulative number of comments by the user on the subreddit.
    Note we only consider edges with existing subreddit_ids.

    Returns dictionary containing edges weighted by comments and
    and a set of unique users.
    """
    comment_weights = defaultdict(int) # edge (user, subreddit_id) -> comment_count
    users = set() # unique users
    for foldername, subdirlist, filelist in os.walk(dirname, topdown=False):
        for fname in filelist:
            if fname.startswith('RC_'):
                # Parse filename for date information
                _, yyyymm = fname.split('RC_')
                yyyy, mm = yyyymm.split('-')

                # Parse the file for edge weights
                with open(os.path.join(dirname, fname)) as f:
                    for line in f:
                        user, subreddit_id, comment_count = line.split()
                        if subreddit_id not in subreddit_ids:
                            continue
                        users.add(user)
                        comment_weights[(user, subreddit_id)] += int(comment_count)
    return comment_weights, users

##############################################
# Main Functions
##############################################
subreddit_names, subreddit_ids = read_subreddit_ids(subreddit_id_file) # subreddit_id -> subreddit
comment_weights, users = read_subreddit_comments(comment_dir, subreddit_ids)
print(len(subreddit_ids))
print(len(users))
