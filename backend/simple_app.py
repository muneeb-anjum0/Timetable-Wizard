"""
Minimal Flask app for Railway deployment testing
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'status': 'ok',
        'message': 'Timetable Wizard API is running (simple mode)',
        'port': os.environ.get('PORT', 'unknown'),
        'mode': 'fallback'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'mode': 'fallback'})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Simple app test endpoint working'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting simple Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)