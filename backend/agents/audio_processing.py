# import speech_recognition as sr
# from agents.hate_speech_agent import HateSpeechDetectionAgent
# from agents.retriever_agent import HybridRetrieverAgent
# from agents.reasoning_agent import PolicyReasoningAgent
# from agents.action_agent import ActionRecommenderAgent
# from config import Config
# from utils.logging_utils import setup_logging
# import logging

# from pydub import AudioSegment
# import os
# import tempfile

# setup_logging()
# logger = logging.getLogger(__name__)

# class AudioProcessingAgent:
#     def __init__(self):
#         self.recognizer = sr.Recognizer()
#         self.hate_speech_agent = HateSpeechDetectionAgent()
#         self.retriever_agent = HybridRetrieverAgent()
#         self.reasoning_agent = PolicyReasoningAgent()
#         self.action_agent = ActionRecommenderAgent()

#     def _ensure_wav(self, audio_file_path: str) -> str:
#         """Convert MP3 to WAV if needed, return path to WAV file."""
#         ext = os.path.splitext(audio_file_path)[1].lower()
#         if ext == ".wav":
#             return audio_file_path
#         elif ext == ".mp3":
#             sound = AudioSegment.from_mp3(audio_file_path)
#             tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
#             sound.export(tmp_wav.name, format="wav")
#             return tmp_wav.name
#         else:
#             raise ValueError("Unsupported audio format. Please upload a WAV or MP3 file.")

#     def transcribe_audio(self, audio_file_path: str) -> str:
#         """Transcribe an audio file to text using Google Speech Recognition."""
#         try:
#             wav_path = self._ensure_wav(audio_file_path)
#             with sr.AudioFile(wav_path) as source:
#                 audio = self.recognizer.record(source)
#                 text = self.recognizer.recognize_google(audio)
#                 logger.info(f"Transcription successful: {text}")
#                 # Clean up temp wav if converted
#                 if wav_path != audio_file_path and os.path.exists(wav_path):
#                     os.remove(wav_path)
#                 return text
#         except sr.UnknownValueError:
#             logger.warning("Could not understand audio.")
#             return ""
#         except sr.RequestError as e:
#             logger.error(f"Speech recognition error: {str(e)}")
#             return ""
#         except Exception as e:
#             logger.error(f"Error during audio transcription: {str(e)}")
#             return ""

#     def analyze_audio(self, audio_file_path: str, include_policies: bool = True, include_reasoning: bool = True) -> dict:
#         """Transcribe audio and run the full analysis pipeline."""
#         transcription = self.transcribe_audio(audio_file_path)
#         if not transcription:
#             return {
#                 "success": False,
#                 "error": "Could not transcribe audio or audio was empty."
#             }

#         # Step 1: Classification
#         classification_result = self.hate_speech_agent.classify_text(transcription)
#         if not classification_result.get("success"):
#             return {
#                 "success": False,
#                 "error": classification_result.get("message", "Classification failed.")
#             }

#         response_data = {
#             "transcription": transcription,
#             "classification": classification_result
#         }

#         # Step 2: Retrieve policies (if requested)
#         if include_policies:
#             retrieval_result = self.retriever_agent.retrieve_policies(
#                 transcription,
#                 classification_result["label"]
#             )
#             if retrieval_result.get("success"):
#                 response_data["retrieved_policies"] = retrieval_result["documents"]

#         # Step 3: Generate reasoning (if requested)
#         if include_reasoning:
#             reasoning_result = self.reasoning_agent.generate_reasoning(
#                 transcription,
#                 classification_result,
#                 response_data.get("retrieved_policies", [])
#             )
#             if reasoning_result.get("success"):
#                 response_data["reasoning"] = reasoning_result["reasoning"]

#         # Step 4: Recommend action
#         action_result = self.action_agent.recommend_action(
#             classification_result,
#             reasoning_result if include_reasoning else {}
#         )
#         if action_result.get("success"):
#             response_data["recommended_action"] = action_result

#         response_data["success"] = True
#         return response_data