from MicroCore.components.types import FileContent
from MicroCore.core import MicroCore
from MicroCore._deploy import deploy_using_config,launch_api

import io
from typing import Dict,Any
from pydantic import BaseModel, Field
from pydub import AudioSegment

class AudioPitchEnhancementInput(BaseModel):
    audio_file: FileContent = Field(..., mime_type="audio/*")
    audio_format: Dict[str, Any] = Field(...,mime_type="application/json")

class AudioPitchEnhancementOutput(BaseModel):
    output_audio_file: FileContent = Field(
        ..., 
        mime_type="audio/*", 
        description="Higher pitch audio"
    )
    output_meta: Dict[str, Any]= Field(...,mime_type="application/json")

def audio_pitch_enhancement(
    input: AudioPitchEnhancementInput,
) -> AudioPitchEnhancementOutput:
    
    audio = AudioSegment.from_file(io.BytesIO(input.audio_file.as_bytes()), format="mp3")
    
    # Increase pitch by 5 semitones
    modified_audio = audio._spawn(audio.raw_data, overrides={
       "frame_rate": int(audio.frame_rate * 2.0)
    }).set_frame_rate(audio.frame_rate)
    

    audio_byte_array = io.BytesIO()
    modified_audio.export(audio_byte_array, format="mp3")
    
    modified_audio_meta={'key','value'}
    return AudioPitchEnhancementOutput(output_audio_file=audio_byte_array.getvalue(),output_meta = modified_audio_meta)

if __name__ == "__main__":

    service_core = MicroCore(audio_pitch_enhancement) #create the service object here
    # deploy_using_config(ips, "./deploy.yaml") #example to deploy using yaml
    launch_api(service_core,host="0.0.0.0",port=8080)
    
"""
JSON Body for Postman
For the JSON body in Postman, you would encode the audio file in base64 format just like the image. The JSON body would look like this:
    {
  "audio_file": "Base64EncodedStringOfAudioFileHere"
}

Replace "Base64EncodedStringOfAudioFileHere" with the actual base64-encoded audio data.

Encoding Audio to Base64
To encode the audio file to base64, you can use a Python snippet like this:
import base64

with open("audio_file.mp3", "rb") as audio_file:
    base64_string = base64.b64encode(audio_file.read()).decode()

print(base64_string)
"""
