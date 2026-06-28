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
# -----------------------------------
ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")

if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path

if ffprobe_path:
    AudioSegment.ffprobe = ffprobe_path

# -----------------------------------
# PAGE SETTINGS
# -----------------------------------
st.set_page_config(
    page_title="KavyaAI",
    page_icon="🎙️"
)

st.title("🎙️ KavyaAI - Hindi Poetry Narrator")

# -----------------------------------
# USER INPUT
# -----------------------------------
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

output_format = st.selectbox(
    "Output Format",
    [
        "WAV",
        "MP3"
    ]
)

file_name = st.text_input(
    "Output File Name",
    value="kavya_output"
)

# -----------------------------------
# TTS FUNCTION
# -----------------------------------
async def generate_tts(text, voice_name, output_file):
    communicate = edge_tts.Communicate(
        text,
        voice_name
    )
    await communicate.save(output_file)

# -----------------------------------
# GENERATE BUTTON
# -----------------------------------
if st.button("Generate Narration"):

    if poem.strip() == "":
        st.warning("Please enter a poem.")
        st.stop()

    lines = [line for line in poem.split("\n") if line.strip()]

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

    st.success("Narration generated successfully!")

    st.audio(output_file)

    mime_type = (
        "audio/mpeg"
        if extension == "mp3"
        else "audio/wav"
    )

    with open(output_file, "rb") as f:
        st.download_button(
            label=f"Download {output_format}",
            data=f,
            file_name=output_file,
            mime=mime_type
        )