import streamlit as st
import os
import bcrypt
from openai import OpenAI
import numpy as np
import base64
import pytube
import os
import librosa
from pydub import AudioSegment
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import tensorflow as tf
from statistics import mode
from tensorflow import keras
from keras import regularizers
from keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Flatten, Dropout, Dense, Activation)
from streamlit_option_menu import option_menu
import time
import requests  # Dùng để gửi yêu cầu API
import asyncio 
import streamlit.components.v1 as components    
from auth import register_user
from streamlit_cookies_manager import CookieManager
import base64
import time
from tensorflow.keras.layers import (Input, Add, Dense, Activation, ZeroPadding2D, BatchNormalization, 
                                     Flatten, Conv2D, AveragePooling2D, MaxPooling2D, GlobalMaxPooling2D,
                                     Dropout)
from tensorflow.keras.layers import BatchNormalization


def classify_music():
    st.markdown("<h1 style='text-align: center; color: white;'>Music Genre Recognition</h1>", unsafe_allow_html=True)

    # Upload file mp3
    st.write("## Upload an MP3 file to classify:")
    mp3_file = st.file_uploader("Upload an audio file", type=["mp3"], label_visibility="collapsed")    
    

    if mp3_file is not None:
        st.write("**Play the song below:**")
        st.audio(mp3_file, "audio/mp3")

        def convert_mp3_to_wav(music_file):
            sound = AudioSegment.from_mp3(music_file)
            sound.export("music_file.wav", format="wav")

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

        def predict(image_data, model):
            image = img_to_array(image_data)
            image = np.reshape(image, (1, 100, 200, 4))
            prediction = model.predict(image / 255)
            prediction = prediction.reshape((10,))
            class_label = np.argmax(prediction)
            return class_label, prediction

        class_labels = ['blues', 'classical', 'country', 'disco', 'hiphop',
                        'jazz', 'metal', 'pop', 'reggae', 'rock']

        model = GenreModel(input_shape=(100, 200, 4), classes=10)
        model.load_weights("music_genre_recog_model.h5")

        with st.spinner("🔍 Analyzing music genre..."):
            time.sleep(2)

        convert_mp3_to_wav(mp3_file)
        audio_full = AudioSegment.from_wav('music_file.wav')

        class_labels_total = []
        predictions_total = []

        for w in range(int(round(len(audio_full) / 3000, 0))):
            audio_3sec = audio_full[3 * w * 1000: 3 * (w + 1) * 1000]
            audio_3sec.export(out_f="audio_3sec.wav", format="wav")

            image_path = f"melspectrogram_{w}.png"

            try:
                y, sr = librosa.load("audio_3sec.wav")
                mel_spec = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr))
                plt.figure(figsize=(10, 5))
                plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])
                librosa.display.specshow(mel_spec, x_axis="time", y_axis='mel', sr=sr)
                plt.margins(0)
                plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
                plt.close()
            except Exception as e:
                st.warning(f"❌ Không thể tạo ảnh cho đoạn {w}: {e}")
                continue

            if not os.path.exists(image_path):
                st.warning(f"❌ Ảnh {image_path} không tồn tại. Bỏ qua.")
                continue

            try:
                image_data = load_img(image_path, color_mode='rgba', target_size=(100, 200))
            except Exception as e:
                st.warning(f"❌ Lỗi khi load ảnh {image_path}: {str(e)}")
                continue

            class_label, prediction = predict(image_data, model)
            class_labels_total.append(class_label)
            predictions_total.append(prediction)

        if not class_labels_total:
            st.error("Không có dữ liệu để dự đoán.")
            return

        class_label_final = mode(class_labels_total)
        predictions_final = np.mean(predictions_total, axis=0)

        st.success(f"✅ The genre of your song is: **{class_labels[class_label_final]}**")

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#0E0808')
        ax.set_facecolor('#0E0808')
        ax.bar(class_labels, predictions_final, color=cm.viridis(np.linspace(0, 1, len(class_labels))))
        ax.set_xlabel("Music Genre", color='white', fontsize=16)
        ax.set_ylabel("Prediction Probability", color='white', fontsize=16)
        ax.set_title("Genre Prediction Probability Distribution", color='white', fontsize=18)
        ax.set_xticklabels(class_labels, rotation=45, color='white', fontsize=14)
        ax.grid(False)

        st.pyplot(fig)





