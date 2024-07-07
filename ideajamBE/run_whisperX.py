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
            formatted_output.append("")
            current_speaker = entry['speaker']
            current_text = entry['text']
    
    # Append the last collected text
    formatted_output.append(f"{current_speaker}: {current_text}")
    
    return "\n".join(formatted_output)

def transcribe_and_format(audio_file, device="cuda", batch_size=16, compute_type="float16", model_size="large-v2"):
    # Load the model
    model = whisperx.load_model(model_size, device, compute_type=compute_type)
    
    # Save model to local path (optional)
    # Specify the relative path from the current working directory
    relative_path = "model_data"
    model_dir = os.path.join(os.getcwd(), relative_path)
    model = whisperx.load_model(model_size, device, compute_type=compute_type, download_root=model_dir)

    # Load the audio file
    audio = whisperx.load_audio(audio_file)
    
    # Transcribe with original whisper (batched)
    result = model.transcribe(audio, batch_size=batch_size)

    # Delete model if low on GPU resources
    # gc.collect(); torch.cuda.empty_cache(); del model

    # Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    # Delete model if low on GPU resources
    # gc.collect(); torch.cuda.empty_cache(); del model_a

    # Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token="hf secret key here", device=device)

    # Add min/max number of speakers if known
    diarize_segments = diarize_model(audio)
    # diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

    result = whisperx.assign_word_speakers(diarize_segments, result)

    print(f"\nThis is the json format output of the segments \n {result['segments']}")
    
    # Format the transcription
    formatted_transcription = format_transcription(result["segments"])

    print(f"The formatted transcription is \n{formatted_transcription}")
    
    return formatted_transcription

# Example usage:
# audio_file = "testing.mp3"
# formatted_transcription = transcribe_and_format(audio_file)
# print(formatted_transcription)
