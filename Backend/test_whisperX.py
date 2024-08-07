import whisperx
import gc
import os

def format_transcription(data):
    if not data:
        return ""
    
    formatted_output = []
    current_speaker = data[0]['speaker']
    current_text = data[0]['text']
    
    for entry in data[1:]:
        if entry['speaker'] == current_speaker:
            current_text += " " + entry['text']
        else:
            formatted_output.append(f"{current_speaker}: {current_text}")
            current_speaker = entry['speaker']
            current_text = entry['text']
    
    # Append the last collected text
    formatted_output.append(f"{current_speaker}: {current_text}")
    
    return "\n".join(formatted_output)

device = "cuda"
audio_file = "testing.mp3"
batch_size = 16  # reduce if low on GPU mem
compute_type = "float16"  # change to "int8" if low on GPU mem (may reduce accuracy)

# 1. Transcribe with original whisper (batched)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

# save model to local path (optional)
# Specify the relative path from the current working directory
relative_path = "model_data"
model_dir = os.path.join(os.getcwd(), relative_path)
model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root=model_dir)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)
# print(result["segments"])  # before alignment

# delete model if low on GPU resources
# gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

# print(result["segments"])  # after alignment

# delete model if low on GPU resources
# gc.collect(); torch.cuda.empty_cache(); del model_a

# 3. Assign speaker labels
diarize_model = whisperx.DiarizationPipeline(use_auth_token="hf secret key here", device=device)

# add min/max number of speakers if known
diarize_segments = diarize_model(audio)
# diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

result = whisperx.assign_word_speakers(diarize_segments, result)
# print(diarize_segments)
# print(result["segments"])  # segments are now assigned speaker IDs
# print("\nThis is the result variable at the end\n")
# print(result)
# print("\n\n")

formatted_transcription = format_transcription(result["segments"])
print(formatted_transcription)
