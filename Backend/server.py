from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
import requests
import run_whisperX

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Set the upload folder (replace with your desired upload directory)
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        saved_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_file_path)
        transcription_text = run_whisperX.transcribe_and_format(saved_file_path)
        print("Finished transcribing")
        response = requests.post('http://localhost:5001/transcription', json={'transcription': transcription_text})

        if response.status_code == 200:
            print("Finish Sentimental analysis")
            return jsonify({'message': 'File successfully send to snips', 'processed_data': response.json().get('processed_data')}), 200
        else:
            print("There is error when running sentiment analysis")
            return jsonify({'error': 'Failed to send transcription to App B', 'details': response.json()}), 500
    return jsonify({'error': 'Invalid file format'}), 400


    
def allowed_file(filename):
    # Add any additional file extensions you want to allow here
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp3','mp4'}


if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
