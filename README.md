Naive implementation of simple recommended system for standart MovieLens dataset:
http://grouplens.org/datasets/movielens/

usage:

python recommender.py <path-to-file-with-rating> <path-to-file-with-movies> <path-to-file-with-tags> <-d>

1) firstly it offers you to choose movie id and number of desirable recommendations
2) secondly it offers you to choose user id and number of desirable recommendations
3) and finally it ask you about user id, movie id and number of desirable recommendations

How it works:
1) using movies description it generate simple feature vector based on genres; 
every feature - genres - scaled in range (0,1)
TODO: use tags description
2) using rating provided by user and amount of evaluated movies, their correspondent feature vector
    approximation of ideal movie feature vector is generated 

using etalon feature vectors above we search for closest sorrespondence in global feature vector
and show top N result

3) in case we have user id and movie id - we firstly get separated values of feature vector,
and then combine both values using scale factor for user preferences

TODO: check more adavanced concepts:
    add iterative approach for tuning results by approximate min sum equation (regularized cost function):
        min J (X, Theta ) = sum (ThetaX - Y) + regularization term

