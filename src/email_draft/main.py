#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
import os
from groq import Groq
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.utils import make_chunks
from pathlib import Path

from crews.meeting_minutes_crew.meeting_minutes_crew import MeetingMinutesCrew
from crews.gmail_crew.gmail_crew import GmailCrew

import agentops

load_dotenv()

# Initialize the Groq client
client = Groq()

class MeetingMinutesState(BaseModel):
    transcript: str = ""
    meeting_minutes: str = ""


class MeetingMinutesFlow(Flow[MeetingMinutesState]):

    @start()
    def transcribe_meeting(self):
        print("Transcribing meeting")

        SCRIPT_DIR=os.path.dirname(__file__)
        print(SCRIPT_DIR)
        AUDIO_FILE_PATH = os.path.join(SCRIPT_DIR, "EarningsCall.wav")

        audio=AudioSegment.from_file(AUDIO_FILE_PATH,format="wav")

        #chunk size
        chunk_size = 60000
        chunks = make_chunks(audio,chunk_size)

        ## Full transcrition
        full_transcription = ""

        for i,chunk in enumerate(chunks):
            print(f"Transcribing chunk {i+1} of {len(chunks)}")
            chunk_path=f'chunk_{i}.wav'
            chunk.export(chunk_path,format="wav")

            with open(chunk_path,"rb") as audio_file:
                translation = client.audio.translations.create(
                model="whisper-large-v3",
                prompt="Specify context or spelling",
                temperature=0.0,
                file=audio_file
            )
            full_transcription += translation.text + ' '
            self.state.transcript =full_transcription
            print(f"Transcription: {translation.text}")
        
    @listen(transcribe_meeting)
    def generate_meeting_minutes(self):
        print("Generating meeting minutes")
        crew = MeetingMinutesCrew()
        inputs = {"transcript": self.state.transcript}
        meeting_minutes= crew.crew().kickoff(inputs)
        self.state.meeting_minutes = meeting_minutes
    
    @listen(generate_meeting_minutes)
    def generate_email_draft(self):
        print("Generating email draft")
        crew = GmailCrew()
        inputs = {"body": self.state.meeting_minutes}
        email_draft= crew.crew().kickoff(inputs)
        print(email_draft)


        


def kickoff():
    session=agentops.init(os.getenv("AGENTOPS_API_KEY"))
    meeting_minutes_flow = MeetingMinutesFlow()
    meeting_minutes_flow.plot()
    meeting_minutes_flow.kickoff()
    session.end_session()






if __name__ == "__main__":
    kickoff()
