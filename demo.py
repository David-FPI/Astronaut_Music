import streamlit as st
import streamlit.components.v1 as components

# HTML/CSS cho giao diện
html_code = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astronaut MUSIC | Plateforme de création musicale par IA</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>
        /* CSS cho trang */
        :root {
            --color-primary: #7000FF;
            --color-secondary: #C056FF;
            --color-tertiary: #56EDFF;
            --color-accent: #FF5EED;
            --color-bg-dark: #030014;
            --color-text-primary: #FFFFFF;
            --color-text-secondary: #B8B8B8;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--color-bg-dark);
            color: var(--color-text-primary);
            margin: 0;
            padding: 0;
        }

        .glass {
            background: rgba(20, 10, 35, 0.25);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
        }

        .btn-gradient {
            background: linear-gradient(45deg, var(--color-primary), var(--color-secondary));
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
        }

        .btn-gradient:hover {
            transform: translateY(-3px);
        }

        .text-gradient {
            background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-item {
            padding: 1rem;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        .nav-item:hover {
            background: rgba(112, 0, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="flex min-h-screen">
        <!-- Sidebar -->
        <div class="w-64 glass fixed h-full p-6">
            <div class="text-xl font-bold text-center text-gradient mb-8">ASTRONAUT MUSIC</div>
            <div class="mb-8">
                <div class="text-lg text-white">Thomas Nguyen</div>
                <div class="text-sm text-gray-400">Premium</div>
                <div class="mt-2 text-sm text-gray-400">Credits: <span class="text-gradient">75</span></div>
            </div>
            <nav>
                <div class="nav-item">Welcome</div>
                <div class="nav-item">Create Lyrics</div>
                <div class="nav-item">Feel The Beat</div>
                <div class="nav-item">Classify</div>
                <div class="nav-item">Library</div>
                <div class="nav-item">Payments</div>
            </nav>
            <div class="mt-8">
                <button class="btn-gradient w-full">Logout</button>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 p-6 ml-64">
            <h1 class="text-4xl font-bold text-gradient">Welcome to Astronaut Music</h1>
            <p class="text-gray-400 mt-4">Create exceptional music powered by AI</p>
            
            <!-- Featured Track -->
            <div class="glass p-6 mt-8">
                <h2 class="text-xl font-bold text-gradient">🔥 Featured Track</h2>
                <div class="mt-4">
                    <div class="text-lg font-bold">Cosmic Journey</div>
                    <p class="text-gray-400">A musical journey through the stars and infinite space, with space melodies and galactic rhythms.</p>
                    <div class="flex justify-between text-sm text-gray-400 mt-4">
                        <div>By MarieC</div>
                        <div>03:45</div>
                    </div>
                    <div class="flex gap-4 mt-4">
                        <span class="px-3 py-1 rounded-full text-xs bg-purple-500 text-white">Ambient</span>
                        <span class="px-3 py-1 rounded-full text-xs bg-blue-500 text-white">Electronic</span>
                        <span class="px-3 py-1 rounded-full text-xs bg-pink-500 text-white">Space</span>
                    </div>
                </div>
            </div>

            <!-- Trends this month -->
            <div class="mt-8">
                <h2 class="text-xl font-bold text-gradient">🎵 Trends this month</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
                    <div class="glass p-4">
                        <div class="font-bold">Dancing Stars</div>
                        <div class="text-gray-400">By Alex</div>
                    </div>
                    <div class="glass p-4">
                        <div class="font-bold">Moonlight Sonata AI</div>
                        <div class="text-gray-400">By Sophie</div>
                    </div>
                    <div class="glass p-4">
                        <div class="font-bold">Urban Rhythm</div>
                        <div class="text-gray-400">By Max</div>
                    </div>
                    <div class="glass p-4">
                        <div class="font-bold">Ambient Dreams</div>
                        <div class="text-gray-400">By Julie</div>
                    </div>
                </div>
            </div>

            <!-- Explore genres -->
            <div class="mt-8">
                <h2 class="text-xl font-bold text-gradient">🚀 Explore genres</h2>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
                    <div class="glass p-4 text-center cursor-pointer">
                        <i class="fas fa-guitar text-2xl mb-2 text-gradient"></i>
                        <div>Rock</div>
                    </div>
                    <div class="glass p-4 text-center cursor-pointer">
                        <i class="fas fa-compact-disc text-2xl mb-2 text-gradient"></i>
                        <div>Electronic</div>
                    </div>
                    <div class="glass p-4 text-center cursor-pointer">
                        <i class="fas fa-drum text-2xl mb-2 text-gradient"></i>
                        <div>Hip-Hop</div>
                    </div>
                    <div class="glass p-4 text-center cursor-pointer">
                        <i class="fas fa-music text-2xl mb-2 text-gradient"></i>
                        <div>Classical</div>
                    </div>
                    <div class="glass p-4 text-center cursor-pointer">
                        <i class="fas fa-meteor text-2xl mb-2 text-gradient"></i>
                        <div>Ambient</div>
                    </div>
                    <div class="glass p-4 text-center cursor-pointer">
                        <i class="fas fa-ellipsis-h text-2xl mb-2 text-gradient"></i>
                        <div>More</div>
                    </div>
                </div>
            </div>

            <!-- Now Playing -->
            <div class="fixed bottom-0 left-0 right-0 bg-gray-900 p-4 flex justify-between items-center">
                <div class="flex gap-4">
                    <div class="w-12 h-12 bg-gray-700 rounded-lg">
                        <img src="https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=600&auto=format&fit=crop&q=60" alt="Now Playing" class="w-full h-full object-cover rounded-lg">
                    </div>
                    <div>
                        <div class="text-sm font-bold text-white">Cosmic Journey</div>
                        <div class="text-xs text-gray-400">By MarieC</div>
                    </div>
                </div>
                <audio controls class="w-24">
                    <source src="https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1bab.mp3?filename=ambient-piano-logo-111399.mp3" type="audio/mp3">
                </audio>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Hàm để hiển thị trang chào mừng
def display_welcome_page():
    components.html(html_code, height=800)

# Cấu hình Streamlit
def main():
    # Cài đặt cấu hình trang
    st.set_page_config(page_title="Astronaut Music", layout="wide")
    
    # Sidebar navigation
    st.sidebar.title("Astronaut Music")
    page = st.sidebar.selectbox("Chọn trang", ["Welcome", "Create Lyrics", "Feel The Beat", "Classify", "Library", "Payments"])

    if page == "Welcome":
        display_welcome_page()
    elif page == "Create Lyrics":
        st.write("Tạo lời bài hát")
    elif page == "Feel The Beat":
        st.write("Cảm nhận nhịp điệu")
    elif page == "Classify":
        st.write("Phân loại nhạc")
    elif page == "Library":
        st.write("Thư viện âm nhạc")
    elif page == "Payments":
        st.write("Quản lý thanh toán")

if __name__ == "__main__":
    main()
