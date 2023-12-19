import whisper

model = whisper.load_model("base")
result = model.transcribe("je_veux_pas_y_aller_maman.wav")
print(result["text"])