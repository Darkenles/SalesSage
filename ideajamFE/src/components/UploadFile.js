import React, { useState } from 'react';
import axios from 'axios';
import './UploadFile.css';

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [toDo, setToDo] = useState('');
  const [custSenti, setCustSenti] = useState('');
  const [saleSenti, setSalesSenti] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    try {
      const formData = new FormData();
      formData.append('audio', selectedFile);

      // Replace 'http://localhost:5000/upload' with your actual backend URL
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Upload successful', response.data);

      // Assuming your server returns a JSON object with transcription text
      if (response.data && response.data.processed_data) {
        setTranscription(response.data.processed_data.transcription);
        setToDo(response.data.processed_data.todos);
        setCustSenti(response.data.processed_data["customer sentiment"]);
        setSalesSenti(response.data.processed_data["sales sentiment"]);
      }
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };

  const formatText = (text) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        <br />
      </React.Fragment>
    ));
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!selectedFile}>
        Upload
      </button>
       {transcription && (
         <div className="result-section">
           <h2>Transcription:</h2>
           <div className="result-text">{formatText(transcription)}</div>
         </div>
       )}
       {toDo && (
         <div className="result-section">
           <h2>ToDo List:</h2>
           <div className="result-text">{formatText(toDo)}</div>
         </div>
       )}
       {custSenti && (
         <div className="result-section">
           <h2>Customer sentiment:</h2>
           <div className="result-text">{formatText(custSenti)}</div>
         </div>
       )}
       {saleSenti && (
         <div className="result-section">
           <h2>Sale-person sentiment:</h2>
           <div className="result-text">{formatText(saleSenti)}</div>
         </div>
       )}
    </div>
  );
};

export default UploadForm;