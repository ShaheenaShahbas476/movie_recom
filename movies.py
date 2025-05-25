import pandas as pd
import random

# Define the emotion-to-genre mapping
emotion_to_genre = {
    'Happy': ['Comedy', 'Romance'],
    'Sad': ['Drama', 'Documentary'],
    'Angry': ['Action', 'Thriller'],
    'Surprise': ['Mystery', 'Sci-Fi'],
    'Fear': ['Horror'],
    'Disgust': ['Drama'],
    'Neutral': ['Any']
}

# Define the function to update recommendations
def refresh_recommendations(emotion, num_recommendations, language):
    genres = emotion_to_genre.get(emotion, [])
    if 'Any' in genres:
        genres = list(set(genre for sublist in emotion_to_genre.values() for genre in sublist))

    # Filter movies by genres and language
    filtered_movies = smd[
        smd['genres'].apply(lambda x: any(genre in x for genre in genres)) &
        (smd['original_language'] == language)
    ]

    if emotion == 'Neutral':
        movies_to_recommend = smd[smd['original_language'] == language]['title'].tolist()
        movies_to_recommend = random.sample(movies_to_recommend, min(len(movies_to_recommend), num_recommendations))
    else:
        movies_to_recommend = filtered_movies['title'].tolist()
        if not movies_to_recommend:
            print(f"\n⚠️ No movies found for emotion '{emotion}' in language '{language}'. Showing from all languages instead.")
            filtered_movies = smd[smd['genres'].apply(lambda x: any(genre in x for genre in genres))]
            movies_to_recommend = filtered_movies['title'].tolist()
        movies_to_recommend = random.sample(movies_to_recommend, min(len(movies_to_recommend), num_recommendations))

    # Create a DataFrame to display
    recommendations_df = pd.DataFrame({
        'Title': movies_to_recommend
    })

    print("\n🎬 Recommended Movies:")
    print(recommendations_df)


# Load movie data
def load_data():
    try:
        md = pd.read_csv('Movies/movies_metadata.csv', low_memory=False)

        md = md[md['id'].apply(lambda x: str(x).isdigit())]
        md['id'] = md['id'].astype(int)

        links_small = pd.read_csv('Movies/links_small.csv')
        links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype(int)

        md = md[~md['id'].isin([19730, 29503, 35587])]
        smd = md[md['id'].isin(links_small)]

        smd.loc[:, 'tagline'] = smd['tagline'].fillna('')
        smd.loc[:, 'description'] = smd['overview'].fillna('') + smd['tagline']
        smd.loc[:, 'description'] = smd['description'].fillna('')
        smd.loc[:, 'genres'] = smd['genres'].fillna('')

        return smd
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


if __name__ == "__main__":
    smd = load_data()

    if smd is not None:
        all_movies = list(smd['title'])

        # Show available language codes
        language_names = {
            'en': 'English',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'fr': 'French',
            'es': 'Spanish',
            'ja': 'Japanese'
        }
        print("\n🌐 Available Languages:")
        for code, name in language_names.items():
            print(f"{name} ({code})")

        # Get user input
        emotion = input("\nEnter your emotion (Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral): ").capitalize()
        language = input("Enter language code (e.g., en for English, hi for Hindi, ta for Tamil): ").lower()

        if language not in smd['original_language'].unique():
            print("⚠️ Language not available in dataset. Defaulting to English (en).")
            language = 'en'

        if emotion not in emotion_to_genre:
            print("❌ Invalid emotion. Please enter one of the valid options.")
        else:
            try:
                num_recommendations = int(input("Enter number of movie recommendations: "))
                if num_recommendations <= 0:
                    raise ValueError("Number of recommendations must be positive.")

                # Get recommendations
                refresh_recommendations(emotion, num_recommendations, language)
            except ValueError as e:
                print(f"Invalid input: {e}")
    else:
        print("Failed to load data.")
