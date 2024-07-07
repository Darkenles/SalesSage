import React from 'react';
import './App.css';
// import VoiceRecorder from './components/VoiceRecorder';
import UploadFile from './components/UploadFile';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Sales Sage: Audio Analysis</h1>
        <UploadFile />
      </header>
    </div>
  );
}

export default App;
