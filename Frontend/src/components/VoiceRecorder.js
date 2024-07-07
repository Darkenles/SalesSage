// src/components/VoiceRecorder.js
import React, { useState } from 'react';
import { ReactMic } from 'react-mic';
import axios from 'axios';

const VoiceRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [blobURL, setBlobURL] = useState(null);

  const startRecording = () => {
    setRecording(true);
  };

  const stopRecording = () => {
    setRecording(false);
  };

  const onData = (recordedBlob) => {
    console.log('chunk of real-time data is: ', recordedBlob);
  };

  const onStop = async (recordedBlob) => {
    setBlobURL(recordedBlob.blobURL);

    const formData = new FormData();
    formData.append('file', recordedBlob.blob, 'audio.wav');

    try {
      const response = await axios.post('http://localhost:5000/api/whisper', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
      });

      console.log('Whisper response:', response.data);
    } catch (error) {
      console.error('Error sending audio to Whisper API:', error);
    }
  };

  return (
    <div>
      <ReactMic
        record={recording}
        className="sound-wave"
        onStop={onStop}
        onData={onData}
        strokeColor="#000000"
        backgroundColor="#FF4081"
      />
      <button onClick={startRecording} type="button">Start</button>
      <button onClick={stopRecording} type="button">Stop</button>
      {blobURL && <audio src={blobURL} controls="controls" />}
    </div>
  );
};

export default VoiceRecorder;
