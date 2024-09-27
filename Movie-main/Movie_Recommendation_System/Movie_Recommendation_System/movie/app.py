import streamlit as st
from backend import get_movies_by_cast, get_movies_by_genres, get_movies_by_cast_and_genres, get_movie_recommendations, movies

# Icon & Title
st.set_page_config(
    page_title="CINEMATCH",
    page_icon="CINEMATCH.png"
)

# Add CSS file
with open("style.css") as main_css:
    st.markdown(f"<style>{main_css.read()}</style>", unsafe_allow_html=True)

# Streamlit app
st.text('CINEMATCH')
st.title('Movie Recommendation System')

# Inputs for user to specify actors and genres
cast_names = st.text_input('Enter actor names (Separated by comma):')
genre_names = st.text_input('Enter genres (Separated by comma):')

# Dropdown for movie titles
movie_titles = movies['title_movie'].tolist()
movie_title = st.selectbox('Or, select a movie title for recommendations:', [''] + movie_titles)

# Convert the input strings to lists
cast_names_list = [name.strip() for name in cast_names.split(',') if name.strip()]
genre_names_list = [name.strip() for name in genre_names.split(',') if name.strip()]

# Button to trigger recommendation
if st.button('Get Recommendations'):
    if movie_title:
        recommendations = get_movie_recommendations(movie_title, movies)
        st.write(f"Recommended movies similar to {movie_title}:")
    elif not cast_names_list and not genre_names_list:
        st.write("Please enter at least one actor name or genre.")
    elif not cast_names_list:
        recommendations = get_movies_by_genres(genre_names_list, movies)
        st.write(f"Recommended movies in genres {', '.join(genre_names_list)}:")
    elif not genre_names_list:
        recommendations = get_movies_by_cast(cast_names_list, movies)
        st.write(f"Recommended movies with {', '.join(cast_names_list)}:")
    else:
        recommendations = get_movies_by_cast_and_genres(cast_names_list, genre_names_list, movies)
        st.write(f"Recommended movies with {', '.join(cast_names_list)} in genres {', '.join(genre_names_list)}:")

    # Display the results
    if recommendations:
        # Show a maximum of 10 recommendations
        for movie in recommendations[:10]:
            st.write(movie['title'])
            if movie['poster']:
                st.image(movie['poster'])
            else:
                st.write("Poster not available")
    else:
        if movie_title:
            st.write(f"No movies found similar to {movie_title}.")
        elif not cast_names_list:
            st.write(f"No movies found in genres {', '.join(genre_names_list)}.")
        elif not genre_names_list:
            st.write(f"No movies found with {', '.join(cast_names_list)}.")
        else:
            st.write(f"No movies found with {', '.join(cast_names_list)} in genres {', '.join(genre_names_list)}.")
