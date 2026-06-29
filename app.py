import streamlit as st
import asyncio
import edge_tts
import tempfile
import os
import shutil
import librosa
import soundfile as sf

from pydub import AudioSegment

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
st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e293b 100%
    );
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #374151;
}

/* Buttons */
.stButton button {
    width: 100%;
    height: 55px;
    border-radius: 15px;
    border: none;
    background: linear-gradient(
        90deg,
        #8b5cf6,
        #3b82f6
    );
    color: white;
    font-size: 18px;
    font-weight: bold;
}

/* Text Area */
.stTextArea textarea {
    border-radius: 15px;
    background-color: #1e293b;
    color: white;
    border: 1px solid #374151;
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
    transform: scale(1.02);
    transition: all 0.3s ease;
    box-shadow: 0px 6px 20px rgba(139, 92, 246, 0.5);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
padding:35px;
border-radius:20px;
background:linear-gradient(
90deg,
#8b5cf6,
#3b82f6
);
text-align:center;
margin-bottom:20px;
">
<h1 style="color:white;">
🎙️ Raya Studio
</h1>
<h4 style="color:white;">
Create. Narrate. Inspire.
</h4>
<p style="color:white;">
AI Voice Narrator for Poetry, Stories and Audiobooks
</p>
</div>
""", unsafe_allow_html=True)
# -----------------------------------
# Sidebar
# -----------------------------------
st.sidebar.markdown("## 🎛️ Narration Settings")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🌐 Language")

st.sidebar.markdown("### 🎙️ Voice")

st.sidebar.markdown("### 🎚️ Audio Controls")

st.sidebar.markdown("### 💾 Export")

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

output_format = st.sidebar.selectbox(
    "Output Format",
    [
        "WAV",
        "MP3"
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

# -----------------------------------
# Main Text Area
# -----------------------------------
poem = st.text_area(
    "Enter Text",
    height=400,
    placeholder="""
Write or paste your poem, story or speech here...

यहाँ अपनी कविता, कहानी या भाषण लिखें...
"""
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

st.caption(
    f"📝 {len(poem)} characters | "
    f"{len(poem.split())} words | "
    f"{len(poem.splitlines())} lines"
)

# -----------------------------------
# TTS Function
# -----------------------------------
async def generate_tts(text, voice_name, output_file):
    communicate = edge_tts.Communicate(
        text,
        voice_name
    )
    await communicate.save(output_file)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Characters",
        len(poem)
    )

with col2:
    st.metric(
        "Lines",
        len(poem.splitlines())
    )

with col3:
    estimated = max(
        1,
        len(poem.split()) // 130
    )

    st.metric(
        "Est. Minutes",
        estimated
    )

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

    output_file = f"{file_name}.{extension}"

    try:
        final_audio.export(
            output_file,
            format=extension
        )
    except Exception as e:
        st.error(
            f"Export failed:\n{e}"
        )
        st.stop()

        st.success(
        f"✅ {output_format} narration generated successfully!"
    )

    with st.container(border=True):
        st.subheader("🎧 Preview")
        st.audio(output_file)

        mime_type = (
            "audio/mpeg"
            if extension == "mp3"
            else "audio/wav"
        )

        with open(output_file, "rb") as f:
            st.download_button(
                label=f"📥 Download {output_format}",
                data=f,
                file_name=output_file,
                mime=mime_type
            )

# -----------------------------------
# Footer
# -----------------------------------
st.markdown("---")
st.markdown("---")

st.markdown("""
<div style='text-align:center'>
<h4>🎙️ Raya Studio</h4>
<p>Create. Narrate. Inspire.</p>
<p>Version 3.1</p>
</div>
""", unsafe_allow_html=True)