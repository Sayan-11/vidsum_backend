from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API key from environment variables
OPEN_AI_KEY = os.getenv('API_KEY')

@app.route("/")
def home():
    return "Hello from Flask on Render!"

# Endpoint to fetch captions
@app.route('/captions', methods=['GET'])
def get_captions():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400

    try:
        # Fetch captions using youtube-transcript-api
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        captions = ' '.join([entry['text'] for entry in transcript])
        return jsonify({'captions': captions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to summarize captions using OpenAI
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    captions = data.get('captions')
    if not captions:
        return jsonify({'error': 'Captions are required'}), 400

    try:
        # Call OpenAI API to summarize captions
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer OPEN_AI_KEY'
            },
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Generate concise bullet points summarizing key concepts from video content.'
                    },
                    {
                        'role': 'user',
                        'content': f'Video content: {captions[:4000]}'
                    }
                ],
                'temperature': 0.3
            }
        )
        response.raise_for_status()
        summary = response.json()['choices'][0]['message']['content']
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)