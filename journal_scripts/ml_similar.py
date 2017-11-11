"""

Output from this script is the following:

1.0000 Night of the Living Dead (1968) (id=968)
0.4763 Halloween (1978) (id=1982)
0.4463 Invasion of the Body Snatchers (1956) (id=2664)
0.4170 Evil Dead, The (1981) (id=4105)
0.3997 Nightmare on Elm Street, A (1984) (id=1347)
0.3735 Evil Dead II (Dead by Dawn) (1987) (id=1261)
0.3672 Exorcist, The (1973) (id=1997)
0.3611 Carrie (1976) (id=1345)
0.3558 King Kong (1933) (id=2366)
0.3489 Psycho (1960) (id=1219)
0.3422 Fly, The (1986) (id=2455)
0.3399 Road Warrior, The (Mad Max 2) (1981) (id=3703)
0.3338 Thing, The (1982) (id=2288)
0.3170 Birds, The (1963) (id=1333)
0.3143 Rosemary's Baby (1968) (id=2160)
0.3039 Planet of the Apes (1968) (id=2529)
0.3005 Blue Velvet (1986) (id=2076)
0.2967 Alien (1979) (id=1214)
0.2947 Gremlins (1984) (id=2003)
0.2885 Omen, The (1976) (id=1350)

1.0000 Dirty Dancing (1987) (id=1088)
0.5751 Pretty Woman (1990) (id=597)
0.5457 Flashdance (1983) (id=2942)
0.5426 Ghost (1990) (id=587)
0.5142 Bodyguard, The (1992) (id=3257)
0.5039 Grease (1978) (id=1380)
0.4935 Sister Act (1992) (id=3247)
0.4581 Top Gun (1986) (id=1101)
0.4558 Free Willy (1993) (id=455)
0.4411 Runaway Bride (1999) (id=2724)
0.4283 Grease 2 (1982) (id=1381)
0.4187 Father of the Bride Part II (1995) (id=5)
0.4179 St. Elmo's Fire (1985) (id=2146)
0.4153 League of Their Own, A (1992) (id=3255)
0.4146 Net, The (1995) (id=185)
0.4144 10 Things I Hate About You (1999) (id=2572)
0.4131 Casper (1995) (id=158)
0.4127 Miss Congeniality (2000) (id=4025)
0.4107 First Knight (1995) (id=168)
0.4050 Robin Hood: Prince of Thieves (1991) (id=1027)

1.0000 Ferris Bueller's Day Off (1986) (id=2918)
0.4202 Breakfast Club, The (1985) (id=1968)
0.3839 WarGames (1983) (id=6979)
0.3740 Weird Science (1985) (id=2134)
0.3722 Wayne's World (1992) (id=3253)
0.3625 Stripes (1981) (id=1663)
0.3590 Sixteen Candles (1984) (id=2144)
0.3501 Bill & Ted's Excellent Adventure (1989) (id=4571)
0.3488 Caddyshack (1980) (id=3552)
0.3423 Animal House (1978) (id=3421)
0.3395 Fast Times at Ridgemont High (1982) (id=3210)
0.3383 Ghostbusters (a.k.a. Ghost Busters) (1984) (id=2716)
0.3361 St. Elmo's Fire (1985) (id=2146)
0.3348 Better Off Dead... (1985) (id=1257)
0.3347 Big (1988) (id=2797)
0.3326 Stand by Me (1986) (id=1259)
0.3313 Vacation (1983) (id=2795)
0.3297 Back to the Future (1985) (id=1270)
0.3291 Goonies, The (1985) (id=2005)
0.3243 Lost Boys, The (1987) (id=4128)
"""

import collections
from scipy.stats import pearsonr

path_titles = '/Users/a558989/Downloads/ml-10M100K/movies.dat'
path_ratings = '/Users/a558989/Downloads/ml-10M100K/ratings.dat'

def main(target_id):
    # read in titles
    titles = read_titles(path_titles)
    
    # map from movie id to list of ratings for star wars
    every_x = collections.defaultdict(list)
    
    # map from movie id to list of ratings for other movies
    every_y = collections.defaultdict(list)

    # loop over each user
    for user_dict in read_users(path_ratings):        
        # skip users who haven't rated the movie.
        if target_id not in user_dict:
            continue

        for movie_id in user_dict:
            rating_x = user_dict[target_id]
            rating_y = user_dict[movie_id]
            every_x[movie_id].append(rating_x)
            every_y[movie_id].append(rating_y)

    # calculate correlations for each movie
    correlations = {}
    for movie_id in every_x:
        if len(every_x[movie_id]) >= 1000:
            r_s, p = pearsonr(every_x[movie_id], every_y[movie_id])
            correlations[movie_id] = r_s
        
    for movie_id in sorted(correlations, key=correlations.get, reverse=True)[:20]:
      print('%.4f %s (id=%d)' % (correlations[movie_id], titles[movie_id], movie_id))
    
def read_users(path):
    user_ratings = {}     # dictionary from movie id to user rating
    prev_user_id = -1     #  user id
    
    for line in open(path):
        tokens = line.split('::')    # tokens is a list of the four values in each record
        user_id = int(tokens[0])
        movie_id = int(tokens[1])
        rating = float(tokens[2])
            
        # if the current line represents a new user, process the previous user's ratings
        if user_id != prev_user_id and len(user_ratings) > 0:
            # this tells Python to use the value of user_ratings 
            # for the next iteration of the for loop at the bottom of this cell
            yield user_ratings
            
            # mark new user as current user, clear out old user's ratings
            user_ratings.clear()
            prev_user_id = user_id        
        
        # record user rating
        user_ratings[movie_id] = rating
        prev_id = user_id
    
    # process the very last user in the file
    yield user_ratings

def read_titles(path):
    """
        Read in the movie ids and their associated titles.
        Returns a hashtable containing the association.
        Note that the ids are ints.  
    """
    titles = {}
    for line in open(path, 'r'):
        tokens = line.split('::')
        if len(tokens) >= 2:
            (id, title) = tokens[:2]
            titles[int(id)] = title
    return titles

main(968)
main(1088)
main(2918)
