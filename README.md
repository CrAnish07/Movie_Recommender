# Movie Recommender System

A Streamlit‑based movie recommender that lets you:

- Get **content‑based** recommendations by selecting a movie  
- Get **genre‑based** recommendations sorted by **Rating(vote_average)** or **popularity**  
- See movie posters fetched live from TMDb

---
## Project Structure

```
Movie_Recommender/
├── app.py
├── Movie_Recommender.ipynb
├── requirements.txt
├── tmdb_5000_credits.csv
├── tmdb_5000_movies.csv
├── movies_dict.pkl
├── similarity.pkl
└── README.md
```
---

## ⚙️ Prerequisites

- Python 3.8 or higher  
- A free TMDb API key (signup at https://www.themoviedb.org/settings/api)  
- [Kaggle CLI](https://github.com/Kaggle/kaggle-api) configured with your credentials  

---
## 🛠 Installation & Setup

1. **Clone the repo**

    ```bash
    git clone https://github.com/CrAnish07/Movie_Recommender.git
    cd Movie_Recommender
    ```

2. **Install Python dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Download the TMDb metadata**  
   This will download and unzip the Kaggle dataset into your `~/Downloads` folder:

    ```bash
    #!/bin/bash
    curl -L -o ~/Downloads/tmdb-movie-metadata.zip \
      https://www.kaggle.com/api/v1/datasets/download/tmdb/tmdb-movie-metadata
    unzip ~/Downloads/tmdb-movie-metadata.zip -d ~/Downloads
    cp ~/Downloads/tmdb_5000_*.csv .
    ```

4. **Generate the pickled data**  
   Open and run the notebook to create `movies_dict.pkl` and `similarity.pkl`:

    ```bash
    jupyter notebook Movie_Recommender.ipynb
    ```

   – After running all cells you’ll see `movies_dict.pkl` and `similarity.pkl` in the cwd.

5. **Configure your TMDb API key**  
   Create a file named `.env` in the project root:

    ```bash
    echo "TMDB_API_KEY=YOUR_API_KEY_HERE" > .env
    ```

   Replace `YOUR_API_KEY_HERE` with your actual TMDb API key.

---
