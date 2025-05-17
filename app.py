import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import ast

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

movies_data = pd.read_csv('tmdb_5000_movies.csv')

def extract_genres(genre_str):
    genres = ast.literal_eval(genre_str)
    return [genre['name'] for genre in genres]

movies_data['genres_list'] = movies_data['genres'].apply(extract_genres)

all_genres = sorted(list({genre for sublist in movies_data['genres_list'] for genre in sublist}))


def fetch_poster(movie_id):
    try:
        url = f"http://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if not poster_path:
            return "https://via.placeholder.com/500x750?text=No+Image"
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters


def recommend_by_vote_average(selected_genre):
    filtered = movies_data[movies_data['genres_list'].apply(lambda x: selected_genre in x)]
    top_movies = filtered.sort_values(by='vote_average', ascending=False).drop_duplicates(subset='title').head(5)
    titles = top_movies['title'].tolist()
    posters = [fetch_poster(mid) for mid in top_movies['id']]
    return titles, posters

def recommend_by_popularity(selected_genre):
    filtered = movies_data[movies_data['genres_list'].apply(lambda x: selected_genre in x)]
    top_movies = filtered.sort_values(by='popularity', ascending=False).drop_duplicates(subset='title').head(5)
    titles = top_movies['title'].tolist()
    posters = [fetch_poster(mid) for mid in top_movies['id']]
    return titles, posters


movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    'Select Movie For Recommandation',
    movies['title'].values
)

if st.button('Recommend'):
    name, poster = recommend(selected_movie_name)
    
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(name[0])
        st.image(poster[0])
    with col2:
        st.text(name[1])
        st.image(poster[1])

    with col3:
        st.text(name[2])
        st.image(poster[2])
    with col4:
        st.text(name[3])
        st.image(poster[3])
    with col5:
        st.text(name[4])
        st.image(poster[4])


st.write("---")
st.subheader("Genre-Based Recommendations")

# Vote Average Section
st.markdown("### Recommend by Rating")
selected_genre_vote = st.selectbox("Select Genre for Rating-Based Recommendation", all_genres, key="vote_genre")
if st.button("Recommend by Rating"):
    names, posters = recommend_by_vote_average(selected_genre_vote)
    st.markdown("#### Top 5 Movies by Rating")
    cols = st.columns(5)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])

# Popularity Section
st.markdown("### Recommend by Popularity")
selected_genre_pop = st.selectbox("Select Genre for Popularity-Based Recommendation", all_genres, key="pop_genre")
if st.button("Recommend by Popularity"):
    names, posters = recommend_by_popularity(selected_genre_pop)
    st.markdown("#### Top 5 Movies by Popularity")
    cols = st.columns(5)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])

