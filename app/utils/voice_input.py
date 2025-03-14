# import speech_recognition as sr


# def get_voice_input() -> str:
#     """
#     Captures voice input and returns the transcribed text.
#     """
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening for voice input...")
#         audio = recognizer.listen(source)

#         try:
#             text = recognizer.recognize_google(audio)
#             print(f"Recognized Text: {text}")
#             return text
#         except sr.UnknownValueError:
#             return "Sorry, I could not understand the audio."
#         except sr.RequestError as e:
#             return f"Error with speech recognition service: {str(e)}"
