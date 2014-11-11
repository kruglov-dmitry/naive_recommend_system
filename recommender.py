import sys,os
from collections import defaultdict
from operator import itemgetter
from itertools import islice

class User_Rating (object):
    def __init__(self, UserID = -1, MovieID = -1, Rating = -1 ):
        self.UserID = UserID 
        self.MovieID = MovieID 
        self.Rating = Rating 
    def __str__(self):
        return str ( self.UserID ) + " " + str(self.MovieID) + " " + str(self.Rating) + os.linesep

class Movie (object):
    def __init__(self, MovieID = -1, Genres = [], Title ="" ):
        self.MovieID = MovieID 
        self.Genres = Genres
        self.Title = Title
    def __str__(self):
        str_view = str(self.MovieID) + os.linesep
        for g in self.Genres:
            str_view += g +" "
        str_view += os.linesep + self.Title
        return str_view

class Movie_Feature(object):
    def __init__(self, MovieID = -1, Genres = {}, Weight = -1 ):
        self.MovieID = MovieID 
        self.Genres = Genres
        self.Weight = Weight

        if ( len(Genres) > 0 ):
            self_binary = 0
            iter_num = len(self.Genres)-1
            for f in self.Genres:
                if self.Genres[f] > 0.0:
                    self_binary += 1*(10**iter_num)
                iter_num -= 1
            self.Binary_Feature = self_binary
        else:
            self.Binary_Feature = 0
    def __str__(self):
        string_representation = "MovieID: " + str(self.MovieID) + os.linesep
        string_representation += "Weight: " + str(self.Weight) + os.linesep
        for key in self.Genres:
            string_representation += key +" - "+ str(self.Genres[key]) + " "
        string_representation += os.linesep + str ( self.Binary_Feature ).zfill(dimension ) + os.linesep

        return string_representation

# based on dataset description
# ignore possible mistake in dataset
canonical_genres = [
            'Action',
            'Adventure',
            'Animation',
            'Children',
            'Comedy',
            'Crime',
            'Documentary',
            'Drama',
            'Fantasy',
            'Film-Noir',
            'Horror',
            'Musical',
            'Mystery',
            'Romance',
            'Sci-Fi',
            'Thriller',
            'War',
            'Western',
            'IMAX']
dimension = len ( canonical_genres )
debug_flag = "-d"
debug_enabled = False
user_scale_factor = 2
#all_genres = set()

acceptable_diff = 333333333333333333    # 0.3 for every genres

def usage():
    print "###########################################################"
    print "Usage:"
    print "python recommender.py rating.dat movies.dat tags.dat"
    print "\trating.dat - format UserID::MovieID::Rating::Timestamp"
    print "\tmovies.dat - format MovieID::Title::Genre1|Genre2|..."
    print "\ttags.dat - format UserID::MovieID::Tag::Timestamp"
    print "\t -d - debug mode on| by default no debug messages printed"
    print "###########################################################"
    sys.exit()

def load_movie_ratings ( file_with_rating):
    
    # format UserID::MovieID::Rating::Timestamp
    with open( file_with_rating ) as f:
        d1 = defaultdict(list)
        for line in f:
            list_of_fields = line.split('::')
            new_user = User_Rating()
            new_user.UserID     = int(list_of_fields[0])
            new_user.MovieID    = int(list_of_fields[1])
            new_user.Rating     = float(list_of_fields[2])
            d1[new_user.UserID].append ( new_user )
            if debug_enabled:
                if new_user.UserID > 13:
                    print "NOTE !!!13!!!"
                    break;
            
            
    list_of_ratings = dict((k, tuple(v)) for k, v in d1.iteritems())
    return list_of_ratings

def load_movies ( file_with_movies ):
    list_of_movies = {}
    # format MovieID::Title::Genre1|Genre2|Genre3...
    with open( file_with_movies ) as f:
        for line in f:
            list_of_fields = line.split('::')
            new_movie = Movie()
            new_movie.MovieID = int(list_of_fields[0])
            new_movie.Title= list_of_fields[1]
            list_of_genres = list_of_fields[2].split('|')
            list_of_genres [-1] = list_of_genres [-1].strip()

            should_continue = True
            for i in list_of_genres:
                if i in canonical_genres:
                    should_continue = False
                    break

            if should_continue:
                continue

            new_movie.Genres = list_of_genres
            #for g in list_of_genres:
            #    if g not in all_genres:
            #        all_genres.add(g)
            list_of_movies[new_movie.MovieID ] = new_movie
            #list_of_movies.append( new_movie )
    #for g in all_genres:
    #    print g + os.linesep
    return list_of_movies
            
def load_tags (file_with_tgs):
    list_of_tags = ()
    # TODO
    # format UserID::MovieID::Tag::Timestamp
    # load file_with_tags
    return list_of_tags

def fill_features ( current_genres, all_genres ):
    features = {}
    sz = len ( current_genres )
    for genr in all_genres:
        if ( any ( substring in genr for substring in current_genres ) ):
            features [ genr ] = (dimension / float(sz)) / float ( dimension )
        else:
            features [ genr ] = 0.0
    return features

def generate_feature_vector ( list_of_movies, list_of_tags ):

    feature_vector = []
    
    for movie_id in list_of_movies:
        cur_weight = 0.0
        movie = list_of_movies[movie_id]
        genres = movie.Genres

        features = fill_features ( genres, canonical_genres )
        cur_weight = sum( features.itervalues() )
        
        new_feature = Movie_Feature(movie_id, features, cur_weight )
        feature_vector.append(new_feature)

    if debug_enabled:
        print "BEFORE"
        for features in feature_vector:
            print features
            break

    # fixme to speed up - use key getter?
    feature_vector.sort(key = lambda x: x.Binary_Feature)
    
    if debug_enabled:
        print "AFTER"
        for features in feature_vector:
            print features
            break

    return feature_vector

def choose_n_similar_movies_by_id ( n, feature_vector, movie_id ):
    movie = None
    for x in list_of_movies:
        if x == movie_id:
            movie = list_of_movies[x]
            break

    movies_ids = []

    if movie == None:
        print "Can't find movie with ID = " + int (movie_id)
        return None
    
    target_feature = next((x for x in feature_vector if x.MovieID == movie_id), None)

    # primitive vote-scheme
    def my_cmp ( x, y ):

        if x.Binary_Feature == target_feature.Binary_Feature and \
            y.Binary_Feature == x.Binary_Feature:
            return 0

        x_hit = 0
        for x_f in x.Genres:
            if x.Genres[x_f] > 0 and target_feature.Genres[x_f] > 0:
                x_hit += 1

        y_hit = 0
        for y_f in y.Genres:
            if y.Genres[y_f] > 0 and target_feature.Genres[y_f] > 0:
                y_hit += 1

        if x_hit > y_hit:
            return -1
        elif x_hit == y_hit:
            return 0
        else:
            return 1

    if debug_enabled:
        print "BEFORE"
        for features in feature_vector:
            print features
            break

    movies_ids = sorted( feature_vector, cmp = my_cmp )

    if debug_enabled:
        print "AFTER"
        for features in movies_ids:
            print features
            break

    # because we also get original movie
    movies_ids = islice(movies_ids, 0, n + 1)   
    movies_ids = filter (lambda obj: obj.MovieID != movie_id, movies_ids )
    return movies_ids

def Choose_Similar_Movie():
    mov_id = int(raw_input('Input movie ID: '))
    num_of_similar = int(raw_input('Input num of similar movies: '))

    print "You choose movie with id = " + str(mov_id)
    print list_of_movies[mov_id]

    selected_movies = choose_n_similar_movies_by_id ( num_of_similar, feature_vectors, mov_id )

    print "List of " + str(num_of_similar) + " recommended movies:"
    for m in selected_movies:
        print list_of_movies[m.MovieID].Title
        if  debug_enabled:
            print list_of_movies[m.MovieID]

def get_user_preferences( user_id, all_genres ):
    user_ratings = list_of_ratings [ user_id ]

    user_feature_vector = {}
    for genr in all_genres:
        user_feature_vector [ genr ] = 0.0

    for every_rating in user_ratings:
        scale = every_rating.Rating
        movie_id = every_rating.MovieID

        cur_feature = next((x for x in feature_vectors if x.MovieID == movie_id), None)
        for g in all_genres:
            user_feature_vector [ g ] += cur_feature.Genres[g] * scale
        
    total_sum = sum( user_feature_vector.itervalues() )

    if debug_enabled:
        print "TOTAL: " + str(total_sum)
        print user_feature_vector
    
    # scale 
    user_feature_vector.update((x, y * 1 / total_sum) for x, y in user_feature_vector.items())
    
    total_sum = sum( user_feature_vector.itervalues() )
    if debug_enabled:
        print "TOTAL: " + str(total_sum)
        print user_feature_vector

    movie_feature = Movie_Feature ( -1, user_feature_vector, 1.0 )
    return movie_feature 

def choose_n_similar_movies ( n, target_feature ):

    movies_ids = []

    # primitive vote-scheme
    # in this case we care not only how many hits we have 
    # but also how they close to target feature vector
    # aka minimize sum of features differences
    def my_cmp_1 ( x, y ):

        x_hit = {}
        for x_f in x.Genres:
            x_hit[x_f] = abs(x.Genres[x_f] - target_feature.Genres[x_f])**2

        y_hit = {}
        for y_f in y.Genres:
            y_hit[y_f] = abs(y.Genres[y_f] - target_feature.Genres[y_f])**2

        total_sum_x = sum( x_hit.itervalues() )
        total_sum_y = sum( y_hit.itervalues() )

        if total_sum_x < total_sum_y :
            return -1
        elif total_sum_x == total_sum_y :
            return 0
        else:
            return 1

    movies_ids = sorted( feature_vectors, cmp = my_cmp_1 )

    movies_ids = islice(movies_ids, 0, n)   
    return movies_ids

def Choose_Similar_Movie_For_User():
    user_id = int(raw_input('Input user ID: '))
    
    # feature vector of ideal movie for this user
    user_preferences = get_user_preferences ( user_id, canonical_genres )
    
    num_of_similar = int(raw_input('Input num of recommended movies: '))
    
    user_recommened_movie = choose_n_similar_movies ( num_of_similar, user_preferences )
    if debug_enabled:
        print "We determine following features vector for this user:" 
        print user_preferences
    print "List of " + str(num_of_similar) + " recommended movies:"
    for m in user_recommened_movie :
        if debug_enabled:
            print list_of_movies[m.MovieID]
            print next((x for x in feature_vectors if x.MovieID == m.MovieID), None)
        print list_of_movies[m.MovieID].Title

def Choose_Items():
    
    mov_id = int(raw_input('Input movie ID: '))
    movie_features = next((x for x in feature_vectors if x.MovieID == mov_id), None)

    user_id = int(raw_input('Input user ID: '))
    # feature vector of ideal movie for this user
    user_preferences = get_user_preferences ( user_id, canonical_genres )

    if debug_enabled:
        print "movie feature:"
        print movie_features 
        print "user preferences"
        print user_preferences 

    target_features_vector = {}
    # combine two features vector and scale result
    for g in canonical_genres:
        target_features_vector [g] = movie_features.Genres [ g ] + user_preferences.Genres[g] * user_scale_factor
        
    total_sum = sum( target_features_vector.itervalues() )
    
    # scale 
    target_features_vector.update((x, y * 1 / total_sum) for x, y in target_features_vector.items())
   
    num_of_similar = int(raw_input('Input num of movies to be recommended: '))

    target_features = Movie_Feature ( -1, target_features_vector, 1.0 )
    if debug_enabled:
        print "We determine following features vector for this user:" 
        print target_features

    recommended_movies = choose_n_similar_movies ( num_of_similar, target_features )
    print "List of " + str(num_of_similar) + " recommended movies:"
    for m in recommended_movies :
        if debug_enabled:
            print list_of_movies[m.MovieID]
            print next((x for x in feature_vectors if x.MovieID == m.MovieID), None)
        print list_of_movies[m.MovieID].Title


"""

            MAIN

"""

if sys.version_info < (2, 7):
    raise "must use python 2.7"

if len(sys.argv) < 4:
    usage()


if debug_flag in sys.argv:
    debug_enabled = True

list_of_ratings = load_movie_ratings ( sys.argv[1] )
list_of_movies = load_movies ( sys.argv[2] )
list_of_tags = load_tags ( sys.argv[3] )

# generate features vectors for every movie
feature_vectors = generate_feature_vector ( list_of_movies, list_of_tags )

Choose_Similar_Movie()
Choose_Similar_Movie_For_User()
Choose_Items()


