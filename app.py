import streamlit as st
from streamlit.runtime.caching import cache_data
import pickle
import pandas as pd
import requests
import os
# from dotenv import load_dotenv
import ast

# load_dotenv()
# API_KEY = os.getenv("TMDB_API_KEY")

API_KEY = st.secrets["TMDB_API_KEY"]


# movies_data = pd.read_csv('tmdb_5000_movies.csv')
# credits_data = pd.read_csv("tmdb_5000_credits.csv")

@st.cache_data
def load_movie_data():
    return pd.read_csv('tmdb_5000_movies.csv')

@st.cache_data
def load_credits_data():
    return pd.read_csv('tmdb_5000_credits.csv')

movies_data = load_movie_data()
credits_data = load_credits_data()


# def extract_genres(genre_str):
#     genres = ast.literal_eval(genre_str)
#     return [genre['name'] for genre in genres]

# movies_data['genres_list'] = movies_data['genres'].apply(extract_genres)

# all_genres = sorted(list({genre for sublist in movies_data['genres_list'] for genre in sublist}))

@st.cache_data
def extract_and_list_genres(df):
    def extract_genres(genre_str):
        genres = ast.literal_eval(genre_str)
        return [genre['name'] for genre in genres]

    df['genres_list'] = df['genres'].apply(extract_genres)
    all_genres = sorted(list({genre for sublist in df['genres_list'] for genre in sublist}))
    return df, all_genres

movies_data, all_genres = extract_and_list_genres(movies_data)




# def extract_cast(cast_str):
#     try:
#         cast_list = ast.literal_eval(cast_str)
#         return [person['name'] for person in cast_list]
#     except:
#         return []

# credits_data['cast_names'] = credits_data['cast'].apply(extract_cast)

# all_actors = sorted(list({actor for sublist in credits_data['cast_names'] for actor in sublist}))


# def extract_director(crew_str):
#     try:
#         crew_list = ast.literal_eval(crew_str)
#         for person in crew_list:
#             if person['job'] == 'Director':
#                 return person['name']
#     except:
#         return None

# credits_data['director'] = credits_data['crew'].apply(extract_director)

# all_directors = sorted(credits_data['director'].dropna().unique())


@st.cache_data
def enrich_credits(df):
    def extract_cast(cast_str):
        try:
            cast_list = ast.literal_eval(cast_str)
            return [person['name'] for person in cast_list]
        except:
            return []

    def extract_director(crew_str):
        try:
            crew_list = ast.literal_eval(crew_str)
            for person in crew_list:
                if person['job'] == 'Director':
                    return person['name']
        except:
            return None

    df['cast_names'] = df['cast'].apply(extract_cast)
    df['director'] = df['crew'].apply(extract_director)
    return df

credits_data = enrich_credits(credits_data)

all_actors = sorted(list({actor for sublist in credits_data['cast_names'] for actor in sublist}))
all_directors = sorted(credits_data['director'].dropna().unique())




@st.cache_data(show_spinner=False)
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

def recommend_by_cast(selected_actor):
    matched = credits_data[credits_data['cast_names'].apply(lambda x: selected_actor in x)]
    merged = matched.merge(movies_data, on="title")

    top_movies = merged.sort_values(by="vote_average", ascending=False).drop_duplicates(subset='title').head(5)

    titles = top_movies['title'].tolist()
    posters = [fetch_poster(mid) for mid in top_movies['id']]
    return titles, posters

def recommend_by_director(selected_director):
    matched = credits_data[credits_data['director'] == selected_director]
    merged = matched.merge(movies_data, on="title")
    
    top_movies = merged.sort_values(by="vote_average", ascending=False).drop_duplicates(subset='title').head(5)

    titles = top_movies['title'].tolist()
    posters = [fetch_poster(mid) for mid in top_movies['id']]
    return titles, posters



# movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
# movies = pd.DataFrame(movies_dict)
# similarity = pickle.load(open('similarity.pkl', 'rb'))

@st.cache_data
def load_pickle_file(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

movies_dict = load_pickle_file('movies_dict.pkl')
similarity = load_pickle_file('similarity.pkl')
movies = pd.DataFrame(movies_dict)



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


st.write("---")
st.subheader("Actor-Based Recommendations")

selected_actor = st.selectbox("Select Actor", all_actors)

if st.button("Recommend by Actor"):
    names, posters = recommend_by_cast(selected_actor)
    st.markdown(f"#### Top Movies Featuring {selected_actor}")
    cols = st.columns(5)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])


st.write("---")
st.subheader("Director-Based Recommendations")

selected_director = st.selectbox("Select Director", all_directors)

if st.button("Recommend by Director"):
    names, posters = recommend_by_director(selected_director)
    st.markdown(f"#### Top Movies by {selected_director}")
    cols = st.columns(5)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
           
