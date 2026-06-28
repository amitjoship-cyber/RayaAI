import streamlit as st
import asyncio
import edge_tts
import tempfile
import os
import librosa
import soundfile as sf

from pydub import AudioSegment

# FFmpeg paths
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

# -------------------------------
# PAGE SETTINGS
# -------------------------------
st.set_page_config(
    page_title="KavyaAI",
    page_icon="🎙️"
)

st.title("🎙️ KavyaAI - Hindi Poetry Narrator")

# Debug information
st.write(
    "FFmpeg found:",
    os.path.exists(r"C:\ffmpeg\bin\ffmpeg.exe")
)
st.write(
    "FFprobe found:",
    os.path.exists(r"C:\ffmpeg\bin\ffprobe.exe")
)

# -------------------------------
# USER INPUT
# -------------------------------
poem = st.text_area(
    "Enter Hindi Poem",
    height=250,
    placeholder="यहाँ अपनी कविता लिखें..."
)

voice = st.selectbox(
    "Voice",
    [
        "hi-IN-MadhurNeural",
        "hi-IN-SwaraNeural"
    ]
)

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
    "Pause Between Lines (seconds)",
    0.5,
    3.0,
    1.0,
    0.1
)

# -------------------------------
# TTS FUNCTION
# -------------------------------
async def generate_tts(text, voice_name, output_file):
    communicate = edge_tts.Communicate(
        text,
        voice_name
    )
    await communicate.save(output_file)

# -------------------------------
# GENERATE BUTTON
# -------------------------------
if st.button("Generate Narration"):

    if poem.strip() == "":
        st.warning("Please enter a poem.")
        st.stop()

    lines = poem.split("\n")

    final_audio = AudioSegment.empty()

    progress = st.progress(0)

    for i, line in enumerate(lines):

        if line.strip() == "":
            continue

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

            # Speed processing
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

        except Exception as e:
            st.error(
                f"Error processing line:\n{line}\n\n{e}"
            )
            st.stop()

        progress.progress(
            (i + 1) / len(lines)
        )

    # Export as WAV first
    output_file = "kavya_output.wav"

    try:
        final_audio.export(
            output_file,
            format="wav"
        )
    except Exception as e:
        st.error(
            f"Export failed:\n{e}"
        )
        st.stop()

    st.success("Narration generated successfully!")

    st.audio(output_file)

    with open(output_file, "rb") as f:
        st.download_button(
            "Download Audio",
            f,
            file_name="kavya_output.wav",
            mime="audio/wav"
        )