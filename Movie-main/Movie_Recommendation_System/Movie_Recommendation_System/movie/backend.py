import pandas as pd
import ast
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the datasets
movies_path = r"C:\Users\SHIRSHA\Downloads\movie\movie\tmdb_5000_movies.csv"
credits_path = r"C:\Users\SHIRSHA\Downloads\movie\movie\tmdb_5000_credits.csv"

# Load data into separate variables
movies = pd.read_csv(movies_path)
credits = pd.read_csv(credits_path)

# Merge the datasets on 'id' column
movies = movies.merge(credits, left_on='id', right_on='movie_id', suffixes=('_movie', '_credits'))

# Preprocess to extract cast and genres
movies['cast'] = movies['cast'].apply(lambda x: [actor['name'].lower() for actor in ast.literal_eval(x)])
movies['genres'] = movies['genres'].apply(lambda x: [genre['name'].lower() for genre in ast.literal_eval(x)])

# Create a combined features column
movies['combined_features'] = movies.apply(lambda row: ' '.join(row['cast']) + ' ' + ' '.join(row['genres']), axis=1)

# TMDb API settings
TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
BASE_MOVIE_URL = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US"
BASE_POSTER_URL = "https://image.tmdb.org/t/p/w500"

def get_poster_url(movie_id):
    try:
        movie_url = BASE_MOVIE_URL.format(movie_id, TMDB_API_KEY)
        response = requests.get(movie_url)
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return BASE_POSTER_URL + data['poster_path']
        return None
    except Exception as e:
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        return None

def get_movies_by_cast(cast_names, movies_df):
    cast_names = [name.lower() for name in cast_names]
    cast_movies = [
        {'title': row['title_movie'], 'poster': get_poster_url(row['id'])}
        for _, row in movies_df.iterrows()
        if all(cast_name in row['cast'] for cast_name in cast_names)
    ]
    return cast_movies

def get_movies_by_genres(genre_names, movies_df):
    genre_names = [name.lower() for name in genre_names]
    filtered_movies = movies_df[movies_df['genres'].apply(lambda x: all(genre in x for genre in genre_names))]
    genre_movies = [
        {'title': row['title_movie'], 'poster': get_poster_url(row['id'])}
        for _, row in filtered_movies.iterrows()
    ]
    return genre_movies

def get_movies_by_cast_and_genres(cast_names, genre_names, movies_df):
    cast_names = [name.lower() for name in cast_names]
    genre_names = [name.lower() for name in genre_names]
    cast_and_genre_movies = [
        {'title': row['title_movie'], 'poster': get_poster_url(row['id'])}
        for _, row in movies_df.iterrows()
        if all(cast_name in row['cast'] for cast_name in cast_names) and all(genre_name in row['genres'] for genre_name in genre_names)
    ]
    return cast_and_genre_movies

def get_movie_recommendations(movie_title, movies_df):
    cv = CountVectorizer(stop_words='english')
    count_matrix = cv.fit_transform(movies_df['combined_features'])
    
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    
    movie_indices = pd.Series(movies_df.index, index=movies_df['title_movie']).drop_duplicates()
    
    idx = movie_indices[movie_title]
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    
    movie_indices = [i[0] for i in sim_scores]
    
    recommended_movies = [
        {'title': movies_df.iloc[i]['title_movie'], 'poster': get_poster_url(movies_df.iloc[i]['id'])}
        for i in movie_indices
    ]
    
    return recommended_movies