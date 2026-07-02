import streamlit as st
import asyncio
import edge_tts
import tempfile
import os
import shutil
import librosa
import soundfile as sf

from pydub import AudioSegment
from docx import Document
from pypdf import PdfReader

# -----------------------------------
# Auto-detect FFmpeg
# Works on Windows and Streamlit Cloud
# -----------------------------------
ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")

if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
else:
    AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
    AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"

if ffprobe_path:
    AudioSegment.ffprobe = ffprobe_path
else:
    AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
# -----------------------------------
# Voice Library
# -----------------------------------
VOICE_OPTIONS = {
    "Hindi - Madhur (Male)": "hi-IN-MadhurNeural",
    "Hindi - Swara (Female)": "hi-IN-SwaraNeural",
    "English India - Prabhat (Male)": "en-IN-PrabhatNeural",
    "English India - Neerja (Female)": "en-IN-NeerjaNeural",
    "English US - Jenny (Female)": "en-US-JennyNeural",
    "English UK - Ryan (Male)": "en-GB-RyanNeural",
}

# -----------------------------------
# Page Settings
# -----------------------------------
st.set_page_config(
    page_title="Raya Studio",
    page_icon="🎙️",
    layout="wide"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Purple"
st.markdown("""
<style>
            
div[data-testid="stVerticalBlock"] > div:has(.glass-card) {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 20px;
}


.stApp {
    background:
    linear-gradient(
        -45deg,
        #0f172a,
        #7c3aed,
        #3b82f6,
        #0f172a
    );

    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
            
@keyframes gradient {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}
/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(17, 24, 39, 0.9);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.08);
    box-shadow: 5px 0px 30px rgba(0,0,0,0.4);
}

/* Buttons */
.stButton button {
    width: 100%;
    height: 60px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(
    90deg,
    #10b981,
    #06b6d4
    );
    color: white;
    font-size: 20px;
    font-weight: bold;
    box-shadow: 0px 8px 20px rgba(
    16,
    185,
    129,
    0.45
    );
    transition: all 0.3s ease;
}

/* Text Area */
.stTextArea textarea {
    border-radius: 20px;
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(15px);
    color: white;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 15px;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.3);
}

/* Input Boxes */
.stTextInput input {
    border-radius: 10px;
}

/* Select Box */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

/* Slider */
.stSlider {
    padding-top: 10px;
}

/* Success Message */
.stAlert {
    border-radius: 15px;
}
            
.stButton button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0px 12px 30px rgba(
        59,
        130,
        246,
        0.6
    );
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
padding:20px;
border-radius:20px;
box-shadow:0px 8px 25px rgba(0,0,0,0.35);
background:linear-gradient(90deg,#8b5cf6,#3b82f6,#06b6d4);
text-align:center;
margin-bottom:15px;">
            
<h1 style="color:white;font-size:50px;margin-bottom:10px;">
🎙️ Raya Studio
</h1>

<h3 style="color:white;margin-top:0px;margin-bottom:10px;">
Create. Narrate. Inspire.
</h3>

<p style="color:white;font-size:20px;margin-bottom:0px;">
AI Voice Narrator for Poetry, Stories and Audiobooks
</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# Sidebarbar
# -----------------------------------
st.sidebar.markdown("## 🎛️ Narration Settings")
st.sidebar.markdown("---")

#st.sidebar.markdown("### 🌐 Language")

#st.sidebar.markdown("### 🎙️ Voice")

#st.sidebar.markdown("### 🎚️ Audio Controls")

#st.sidebar.markdown("### 💾 Export")


language = st.sidebar.selectbox(
    "Language",
    [
        "Auto Detect",
        "Hindi",
        "English"
    ]
)

input_method = st.sidebar.radio(
    "Input Method",
    [
        "Type",
        "Speak (Coming Soon)",
        "Hinglish Typing (Coming Soon)"
    ]
)

voice_label = st.sidebar.selectbox(
    "Voice",
    list(VOICE_OPTIONS.keys())
)

voice = VOICE_OPTIONS[voice_label]

emotion = st.sidebar.selectbox(
    "Narration Style",
    [
        "Normal",
        "Romantic",
        "Sad",
        "Inspirational",
        "Patriotic",
        "Spiritual"
    ]
)

with st.sidebar.expander("🎚️ Advanced Audio Controls"):

    speed = st.slider(
        "Speed",
        0.5,
        1.5,
        1.0,
        0.05
    )

    pitch = st.slider(
        "Pitch",
        -4,
        4,
        0
    )

    pause = st.slider(
        "Pause Between Lines",
        0.5,
        3.0,
        1.0,
        0.1
    )

background_music = st.sidebar.selectbox(
    "🎵 Background Music",
    [
        "None",
        "Soft Piano",
        "Rain",
        "Meditation"
    ]
)
output_format = st.sidebar.selectbox(
    "Output Format",
    [
        "MP3",
        "WAV"
    ]
)

file_name = st.sidebar.text_input(
    "Output File Name",
    value="RayaStudio_Audio"
)

file_name = (
    file_name
    .replace(".mp3", "")
    .replace(".wav", "")
    .strip()
)

if not file_name:
    file_name = "RayaStudio_Audio"

theme = st.sidebar.selectbox(
    "🎨 Theme",
    [
        "Purple",
        "Blue",
        "Dark"
    ]
)

if theme == "Purple":
    primary1 = "#8b5cf6"
    primary2 = "#3b82f6"
    primary3 = "#06b6d4"

elif theme == "Blue":
    primary1 = "#2563eb"
    primary2 = "#0891b2"
    primary3 = "#06b6d4"

elif theme == "Dark":
    primary1 = "#111827"
    primary2 = "#1f2937"
    primary3 = "#374151"

# -----------------------------------
# TTS Function
# -----------------------------------
async def generate_tts(text, voice_name, output_file):
    communicate = edge_tts.Communicate(
        text,
        voice_name
    )
    await communicate.save(output_file)

# -----------------------------------
# Main Text Area
# -----------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload File",
    type=["txt", "docx", "pdf"],
    key="uploaded_file"
)

if uploaded_file:

    if uploaded_file.name.endswith(".txt"):
        poem = uploaded_file.read().decode("utf-8")

    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        poem = "\n".join(
            para.text
            for para in doc.paragraphs
        )

    elif uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        poem = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                poem += text + "\n"

else:
    poem = ""

poem = st.text_area(
    "Enter Text",
    value=st.session_state.get("sample", poem),
    height=400,
    placeholder="""
Write or paste your poem, story or speech here...

यहाँ अपनी कविता, कहानी या भाषण लिखें...
"""
)
c1, c2 = st.columns([1,1], gap="medium")

with c1:
    if st.button("📝 Load Sample", use_container_width=True):
        st.session_state["sample"] = """
मैं भारत हूँ।
I am the voice of dreams.
This is Raya Studio.
"""
        st.rerun()

with c2:
    if st.button("🗑 Clear Text", use_container_width=True):
        st.session_state.sample = ""
        st.session_state.poem = ""
        st.session_state.uploaded_file = None
        st.rerun()


# -----------------------------------
# Generate Button
# -----------------------------------
if st.button(
    "🎙️ Generate Narration",
    use_container_width=True
):

    if poem.strip() == "":
        st.warning("Please enter some text.")
        st.stop()

    # Emotion presets
    if emotion == "Romantic":
        speed = 0.90
        pitch = -1

    elif emotion == "Sad":
        speed = 0.85
        pitch = -2

    elif emotion == "Inspirational":
        speed = 1.05
        pitch = 1

    elif emotion == "Patriotic":
        speed = 1.10
        pitch = 2

    elif emotion == "Spiritual":
        speed = 0.80
        pitch = -1

    lines = [
        line
        for line in poem.split("\n")
        if line.strip()
    ]

    final_audio = AudioSegment.empty()

    progress = st.progress(0)

    for i, line in enumerate(lines):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        ) as fp:
            tmp_mp3 = fp.name

        asyncio.run(
            generate_tts(
                line,
                voice,
                tmp_mp3
            )
        )

        try:
            y, sr = librosa.load(tmp_mp3)

            if pitch != 0:
                y = librosa.effects.pitch_shift(
                    y,
                    sr=sr,
                    n_steps=pitch
                )

            tmp_wav = tmp_mp3.replace(
                ".mp3",
                "_processed.wav"
            )

            sf.write(
                tmp_wav,
                y,
                sr
            )

            segment = AudioSegment.from_file(
                tmp_wav
            )

            if speed > 1.0:
                segment = segment.speedup(
                    playback_speed=speed
                )

            elif speed < 1.0:
                new_frame_rate = int(
                    segment.frame_rate * speed
                )

                segment = segment._spawn(
                    segment.raw_data,
                    overrides={
                        "frame_rate": new_frame_rate
                    }
                ).set_frame_rate(
                    segment.frame_rate
                )

            final_audio += segment

            final_audio += AudioSegment.silent(
                duration=int(
                    pause * 1000
                )
            )

            try:
                os.remove(tmp_mp3)
                os.remove(tmp_wav)
            except:
                pass

        except Exception as e:
            st.error(
                f"Error processing line:\n{line}\n\n{e}"
            )
            st.stop()

        progress.progress(
            (i + 1) / len(lines)
        )

    extension = output_format.lower()

    if background_music != "None":

        music_file = {
            "Soft Piano": "assets/music/piano.mp3",
            "Rain": "assets/music/rain.mp3",
            "Meditation": "assets/music/meditation.mp3"
        }[background_music]

        bg_music = AudioSegment.from_file(music_file)

    # Lower volume
    bg_music = bg_music - 20
    
    while len(bg_music) < len(final_audio):
        bg_music += bg_music

    bg_music = bg_music[:len(final_audio)]

    final_audio = final_audio.overlay(bg_music)

    extension = output_format.lower()
    output_file = f"{file_name}.{extension}"

try:
    final_audio.export(
        output_file,
        format=extension
    )
except Exception as e:
    st.error(f"Export failed:\n{e}")
    st.stop()

st.balloons()

st.success(
    f"🎉 Your {output_format} narration is ready!"
)

st.markdown("## 🎧 Audio Preview")

with st.container(border=True):
    st.subheader("🎧 Preview")
    st.audio(output_file)

    mime_type = (
        "audio/mpeg"
        if extension == "mp3"
        else "audio/wav"
    )

    st.divider()

    with open(output_file, "rb") as f:
        st.download_button(
            label=f"📥 Download {output_format}",
            data=f,
            file_name=output_file,
            mime=mime_type,
            use_container_width=True
        )

    with st.container(border=True):
        st.subheader("🎧 Preview")
        st.audio(output_file)

        mime_type = (
            "audio/mpeg"
            if extension == "mp3"
            else "audio/wav"
        )

        st.divider()

        with open(output_file, "rb") as f:
            st.download_button(
                label=f"📥 Download {output_format}",
                data=f,
                file_name=output_file,
                mime=mime_type,
                use_container_width=True
            )


st.caption(
    f"📝 {len(poem)} characters | "
    f"{len(poem.split())} words | "
    f"{len(poem.splitlines())} lines"
)

st.info(
"""
💡 Tips

• Paste your poem or story.
• Select a voice and narration style.
• Generate and download your narration.

Supports both English and Hindi.
"""
)

st.markdown("### 📊 Text Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📝 Characters",
        len(poem)
    )

with col2:
    st.metric(
        "📄 Words",
        len(poem.split())
    )

with col3:
    st.metric(
        "⏱ Est. Minutes",
        max(1, len(poem.split()) // 130)
    )




# -----------------------------------
# Footer
# -----------------------------------
st.markdown("---")
st.markdown("---")

st.markdown("""
<div style="
text-align:center;
padding:20px;
opacity:0.8;
">
<h3>🎙️ Raya Studio</h3>
<p>Create. Narrate. Inspire.</p>
<p>Version 3.3 Premium Edition</p>
<p>Made with ❤️ in India</p>
</div>
""", unsafe_allow_html=True)