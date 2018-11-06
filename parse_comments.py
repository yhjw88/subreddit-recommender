import snap
import sys, os
from collections import defaultdict
import matplotlib.pyplot as plt

##############################################
# Data Constants
##############################################
comment_dir = 'data/comments/'
subreddit_name_file = 'data/subredditIdToName'
comment_graph_file = 'data/commentGraph.txt'

##############################################
# Utility Functions
##############################################
def base36decode(number):
    return int(number, 36)

##############################################
# Load Raw Reddit Data
##############################################
def read_subreddit_names(filename):
    """
    Reads in file with global mappings from subreddit ids to names.
    Filters out subreddit names that begin with 'u_'.

    Examples: [subreddit_id subreddit_name]
        ...
        t5_3m6wn hormuz
        t5_bx9mz u_Ubiver
        ...

    Returns a dictionary mapping from id to name and a set of
    unique subreddit ids.
    """
    subreddit_name_dict = {} # id -> subreddit
    with open(filename) as f:
        for line in f:
            subreddit_id, subreddit_name = line.split()
            if subreddit_name.startswith('u_'): # not subreddit!
                continue
            subreddit_name_dict[subreddit_id] = subreddit_name
    return subreddit_name_dict

def read_subreddit_comments(dirname, subreddit_name_dict):
    """
    Reads in files containing user-subreddit commenting counts. Each file
    name is of the format RC_YYYY-MM where YYYY and MM are year and month,
    respectively.

    Examples: [user subreddit_id comment_count]
        ...
        PGHContrarian68 t5_2ve45 4
        TheIncompetenceOfMan t5_2qh33 11
        ...

    Each edge is represented as (user, subreddit_id) and is weighted by
    the cumulative number of comments by the user on the subreddit.
    Note we only consider edges with existing subreddit_ids.

    Returns dictionary containing edges weighted by comments and
    and a set of unique users.
    """
    comment_weights = defaultdict(int) # edge (user, subreddit_id) -> comment_count
    users = set() # unique users
    subreddits_ids = set()
    comment_edges = set()
    for foldername, subdirlist, filelist in os.walk(dirname, topdown=False):
        for fname in filelist:
            if fname.startswith('RC_2018-01'): # formated as RC_YYYY-MM
                # Parse filename for date information
                _, yyyymm = fname.split('_')
                yyyy, mm = yyyymm.split('-')

                # Parse the file for edge weights
                with open(os.path.join(dirname, fname)) as f:
                    for line in f:
                        user, subreddit_id, comment_count = line.split()
                        if subreddit_id not in subreddit_name_dict: # skip non-existent subreddit_ids
                            continue
                        users.add(user)
                        subreddits_ids.add(subreddit_id)
                        comment_edges.add((user, subreddit_id))
                        comment_weights[(user, subreddit_id)] += int(comment_count)
    return comment_weights, comment_edges, users, subreddits_ids

subreddit_name_dict = read_subreddit_names(subreddit_name_file) # subreddit_id -> subreddit
comment_weights, comment_edges, users, subreddit_ids = read_subreddit_comments(comment_dir, subreddit_name_dict) # (user, subreddit_id) -> comment_count

print "Number of unique users: ", len(users)
print "Number of unique subreddits: ", len(subreddit_ids)
print "Number of unique comment edges: ", len(comment_edges)

##############################################
# Construct Node and Edge IDs
##############################################
def generate_node_ids(users, subreddit_ids):
    """
    Generate node ids by assigning each user a consecutive
    integer value in [0, num_users) and each subreddit
    a consecutive integer value in [num_users, num_users+num_subreddits)

    Returns dictionaries of users and subreddit_ids to their corresponding
    node ids.
    """
    num_users = len(users) # = MAX_UID
    num_subreddits = len(subreddit_ids)

    # Iterate through sorted users
    user_node_ids = {} # user -> user_node_id
    users = sorted(users)
    for user_node_id, user in enumerate(users):
        user_node_ids[user] = user_node_id

    # Iterate through sorted subreddit ids
    subreddit_node_ids = {} # subreddit_id -> subreddit_node_id
    subreddit_ids = sorted(subreddit_ids)
    for subreddit_node_id, subreddit_id in enumerate(subreddit_ids):
        subreddit_node_ids[subreddit_id] = num_users + subreddit_node_id # shifted by num_users

    return user_node_ids, subreddit_node_ids

user_node_ids, subreddit_node_ids = generate_node_ids(users, subreddit_ids)

##############################################
# Construct Bipartite User-Subreddit Graph
##############################################
def construct_comment_graph(user_node_ids, subreddit_node_ids, comment_edges):
    """
    Creates a the User-Subreddit bipartite undirected graph where the nodes
    are users and subreddits and the edges between the users and subreddits
    represent when a user has commented on a subreddit.
    """
    # Construct the bipartise graph
    G = snap.PUNGraph.New()

    # Add user node ids
    for user, user_node_id in user_node_ids.iteritems():
        G.AddNode(user_node_id)

    # Add subreddit node ids
    for subreddit_id, subreddit_node_id in subreddit_node_ids.iteritems():
        G.AddNode(subreddit_node_id)

    # Add comment edges
    for user, subreddit_id in comment_edges:
        user_node_id = user_node_ids[user]
        subreddit_node_id = subreddit_node_ids[subreddit_id]
        G.AddEdge(user_node_id, subreddit_node_id)

    return G

G = construct_comment_graph(user_node_ids, subreddit_node_ids, comment_edges)

print "Number of nodes: ", G.GetNodes()
print "Number of edges: ", G.GetEdges()

snap.SaveEdgeList(G, comment_graph_file) # save graph to text file
