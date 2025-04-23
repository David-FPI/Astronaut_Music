import streamlit as st
from streamlit.components.v1 import html
import base64
import os
from supabase import create_client
from dotenv import load_dotenv
import librosa
import numpy as np
import matplotlib.pyplot as plt
import tempfile
from pydub import AudioSegment
import tensorflow as tf
from tensorflow import keras
from statistics import mode
import time
from keras import regularizers
from keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Flatten, Dropout, Dense, Activation)
# Load environment variables
load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set page config (only once at the top)
st.set_page_config(
    page_title="Astronaut MUSIC | AI Music Platform",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS from your HTML
def get_custom_css():
    return """
    <style>
    :root {
        --color-primary: #7000FF;
        --color-secondary: #C056FF;
        --color-tertiary: #56EDFF;
        --color-accent: #FF5EDD;
        --color-bg-dark: #030014;
        --color-bg-card: rgba(20, 10, 35, 0.6);
        --color-text-primary: #FFFFFF;
        --color-text-secondary: #B8B8B8;
    }
    
    /* Main background */
    .stApp {
        background-color: var(--color-bg-dark);
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(112, 0, 255, 0.1) 0%, transparent 30%),
            radial-gradient(circle at 90% 90%, rgba(192, 86, 255, 0.05) 0%, transparent 30%);
        color: var(--color-text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    /* Text gradients */
    .text-gradient {
        background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards */
    .music-card {
        background: var(--color-bg-card);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .music-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        border-color: rgba(112, 0, 255, 0.2);
    }
    
    /* Genre badges */
    .genre-badge {
        background: linear-gradient(45deg, var(--color-primary), var(--color-secondary));
        color: white;
        font-size: 0.7rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 2;
    }
    
    /* Custom audio player */
    .custom-audio {
        width: 100%;
        border-radius: 30px;
        background-color: rgba(40, 40, 40, 0.8);
    }
    
    .custom-audio::-webkit-media-controls-panel {
        background: linear-gradient(45deg, #333333, #1A1A1A);
    }
    
    .custom-audio::-webkit-media-controls-play-button {
        background-color: var(--color-primary);
        border-radius: 50%;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, var(--color-primary), var(--color-secondary));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(112, 0, 255, 0.3);
        background: linear-gradient(45deg, var(--color-secondary), var(--color-primary));
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stFileUploader>div>div {
        background-color: rgba(20, 10, 40, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Loading spinner */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid rgba(112, 0, 255, 0.2);
        border-top: 5px solid var(--color-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    </style>
    """

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Genre classification model
def GenreModel(input_shape=(100, 200, 4), classes=10):
    classifier = Sequential()
    classifier.add(Conv2D(8, (3, 3), input_shape=input_shape, activation='relu'))
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    classifier.add(Conv2D(16, (3, 3), activation='relu'))
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    classifier.add(Conv2D(32, (3, 3), activation='relu'))
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    classifier.add(Conv2D(64, (3, 3), activation='relu'))
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    classifier.add(Conv2D(128, (3, 3), activation='relu'))
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    classifier.add(Flatten())
    classifier.add(Dropout(0.5))
    classifier.add(Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.0001)))
    classifier.add(Dropout(0.25))
    classifier.add(Dense(10, activation='softmax'))
    classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return classifier

# Load pre-trained model
@st.cache_resource
def load_model():
    model = GenreModel(input_shape=(100, 200, 4), classes=10)
    model.load_weights("music_genre_recog_model.h5")
    return model

# Convert MP3 to WAV
def convert_mp3_to_wav(music_file):
    sound = AudioSegment.from_mp3(music_file)
    sound.export("music_file.wav", format="wav")

# Create mel spectrogram
def create_melspectrogram(wav_file):
    y, sr = librosa.load(wav_file)
    mel_spec = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr))
    plt.figure(figsize=(10, 5))
    plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])
    librosa.display.specshow(mel_spec, x_axis="time", y_axis='mel', sr=sr)
    plt.margins(0)
    plt.savefig('melspectrogram.png')

# Predict genre
def predict(image_data, model):
    image = img_to_array(image_data)
    image = np.reshape(image, (1, 100, 200, 4))
    prediction = model.predict(image / 255)
    prediction = prediction.reshape((10,))
    class_label = np.argmax(prediction)
    return class_label, prediction

# Home Page
def show_home():
    st.markdown("""
    <div class="section-header">🔥 Morceaux populaires</div>
    """, unsafe_allow_html=True)
    
    # Fetch public songs from Supabase
    public_songs = supabase.table("songs").select("*").eq("is_public", True).order("created_at", desc=True).limit(4).execute()
    user_profiles = supabase.table("user_profiles").select("id, full_name").execute()
    user_map = {u["id"]: u["full_name"] for u in user_profiles.data}
    
    if public_songs.data:
        cols = st.columns(4)
        for idx, song in enumerate(public_songs.data):
            with cols[idx % 4]:
                title = song.get("title", "Untitled")
                artist = user_map.get(song["user_id"], "Anonymous")
                image = song.get("image_url", "https://via.placeholder.com/300x180.png?text=No+Cover")
                audio = song.get("audio_url")
                
                st.markdown(f"""
                <div class="music-card">
                    <div style="position: relative;">
                        <img src="{image}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 16px 16px 0 0;">
                        <div class="genre-badge">v3.5</div>
                    </div>
                    <div style="padding: 1rem;">
                        <h3 style="font-weight: bold; margin-bottom: 0.5rem;">{title}</h3>
                        <p style="font-size: 0.9rem; color: var(--color-text-secondary);">👤 {artist}</p>
                        <audio controls class="custom-audio" src="{audio}" style="width: 100%; margin-top: 0.5rem;"></audio>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucun morceau public disponible pour le moment.")
    
    st.markdown("""
    <div class="section-header" style="margin-top: 2rem;">🎵 Explorer les genres</div>
    """, unsafe_allow_html=True)
    
    genres = ["Rock", "Electronic", "Hip-Hop", "Classical", "Ambient", "Jazz"]
    cols = st.columns(6)
    for idx, genre in enumerate(genres):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                background: rgba(20, 10, 35, 0.3);
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.05);
            ">
                <div style="
                    width: 50px;
                    height: 50px;
                    background: linear-gradient(45deg, var(--color-primary), var(--color-secondary));
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 1rem auto;
                ">
                    <i class="fas fa-music" style="color: white; font-size: 1.5rem;"></i>
                </div>
                <div>{genre}</div>
            </div>
            """, unsafe_allow_html=True)

# Classify Page
def show_classify():
    st.markdown("""
    <div class="section-header">🔍 Classification de genre musical</div>
    <p style="color: var(--color-text-secondary); margin-bottom: 2rem;">
        Identifiez le genre musical à l'aide de l'IA
    </p>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Téléchargez un fichier audio", type=["mp3", "wav"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        if st.button("Analyser le genre"):
            with st.spinner("Analyse en cours..."):
                # Show loading spinner
                st.markdown("""
                <div style="text-align: center; margin: 2rem 0;">
                    <div class="loading-spinner"></div>
                    <p style="margin-top: 1rem;">L'IA analyse votre musique...</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Process the file
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(uploaded_file.read())
                temp_file.close()
                
                # Convert and analyze
                convert_mp3_to_wav(temp_file.name)
                audio_full = AudioSegment.from_wav('music_file.wav')
                
                # Load model
                model = load_model()
                class_labels = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
                
                class_labels_total = []
                predictions_total = []
                
                # Analyze in 3-second chunks
                for w in range(int(round(len(audio_full) / 3000, 0))):
                    audio_3sec = audio_full[3 * w * 1000: 3 * (w + 1) * 1000]
                    audio_3sec.export("audio_3sec.wav", format="wav")
                    create_melspectrogram("audio_3sec.wav")
                    image_data = load_img('melspectrogram.png', color_mode='rgba', target_size=(100, 200))
                    class_label, prediction = predict(image_data, model)
                    class_labels_total.append(class_label)
                    predictions_total.append(prediction)
                
                # Get final prediction
                class_label_final = mode(class_labels_total)
                predictions_final = np.mean(predictions_total, axis=0)
                
                # Show results
                st.success(f"Genre détecté: **{class_labels[class_label_final].capitalize()}**")
                
                # Show prediction distribution
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(class_labels, predictions_final, color=plt.cm.viridis(np.linspace(0, 1, len(class_labels))))
                ax.set_xlabel("Genres musicaux", color='white')
                ax.set_ylabel("Probabilité", color='white')
                ax.set_title("Distribution des prédictions de genre", color='white')
                ax.tick_params(colors='white')
                ax.grid(False)
                fig.patch.set_facecolor('#030014')
                ax.set_facecolor('#030014')
                
                st.pyplot(fig)

# Main App
def main():
    # Navigation
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 1.5rem; font-weight: bold;">
            <span class="text-gradient">ASTRONAUT</span>
            <div style="color: white;">MUSIC</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Navigation",
        ["Accueil", "Classifier"],
        label_visibility="collapsed"
    )
    
    # Show the selected page
    if page == "Accueil":
        show_home()
    elif page == "Classifier":
        show_classify()

if __name__ == "__main__":
    main()