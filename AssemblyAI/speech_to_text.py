import assemblyai as aai
import streamlit as st
from dotenv import load_dotenv
from agno.models.google import Gemini
import os
from fpdf import FPDF


load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")   
client = Gemini(api_key=google_api_key)        

# Streamlit UI
st.title(" Speech to Text + AI Summary/Explanation")

uploaded_audio = st.file_uploader("Upload your audio file (.mp3, .wav)", type=["mp3", "wav"])
if uploaded_audio is not None:
    with open("temp_audio_file", "wb") as f:
        f.write(uploaded_audio.getbuffer())

    with st.spinner(" Transcribing..."):
        config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
        transcript = aai.Transcriber(config=config).transcribe("temp_audio_file")

    if transcript.status == "error":
        st.error(f" Transcription failed: {transcript.error}")
    else:
        st.success(" Transcription complete")
        st.text_area(" Transcript:", transcript.text, height=200)

        # Export transcription to PDF
        if st.button(" Download transcript PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, transcript.text)
            pdf.output("transcript.pdf")
            with open("transcript.pdf", "rb") as f:
                st.download_button("Download PDF", f, file_name="transcript.pdf")

# GPT choice
choice = st.radio("What do you want the agent to do?", [" Summarize", "Explain in detail"])
if st.button("Run GPT"):
    prompt = f"Summarize the following transcript:\n{transcript.text}" if choice == " Summarize" else f"Explain in detail the following transcript:\n{transcript.text}"

    with st.spinner(" Gemini is thinking..."):
        response = client.chat.completions.create(
            model="gemini-1.5-pro",  #  modèle Gemini, pas gpt-4o
            messages=[
                {"role": "system", "content": "You are an expert transcription assistant."},
                {"role": "user", "content": prompt}
            ]
        )

    gpt_output = response.choices[0].message.content.strip()

    st.success(" Gemini response ready")
    st.text_area(" Gemini Output:", gpt_output, height=300)

    # Export GPT result to PDF
    pdf_gpt = FPDF()
    pdf_gpt.add_page()
    pdf_gpt.set_auto_page_break(auto=True, margin=15)
    pdf_gpt.set_font("Arial", size=12)
    pdf_gpt.multi_cell(0, 10, gpt_output)
    pdf_gpt.output("gemini_output.pdf")
    with open("gemini_output.pdf", "rb") as f:
        st.download_button("Download Gemini Output PDF", f, file_name="gemini_output.pdf")
