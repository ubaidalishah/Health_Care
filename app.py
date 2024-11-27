from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv


# from google.oauth2 import service_account
# import os

# # Assuming you have the credentials file saved locally
# credentials_file_path = '/home/bacha/Desktop/google_cloud_credentials/text-to-speech-442918-f56342ef02f7.json'

# credentials = service_account.Credentials.from_service_account_file(credentials_file_path)


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set OpenAI API key
openai.api_key = os.getenv('MY_API')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('sourceLang', 'en')
    target_lang = data.get('targetLang', 'es')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or use another model such as "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": f"Translate the following text from {source_lang} to {target_lang}."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,  # Adjust max tokens to control length
            temperature=0.3  # Lower temperature for predictable output
        )

        translated_text = response['choices'][0]['message']['content'].strip()

        return jsonify({'translatedText': translated_text})

    except Exception as e:
        return jsonify({'error': str(e)})

from google.cloud import texttospeech
import base64

client = texttospeech.TextToSpeechClient()

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data['translatedText']
    target_lang = data['targetLang']  # Get the target language from the request

    # Map targetLang to the corresponding language code for Google TTS
    language_codes = {
        'af': 'af', 'sq': 'sq', 'am': 'am', 'ar': 'ar', 'hy': 'hy', 'az': 'az',
        'eu': 'eu', 'be': 'be', 'bn': 'bn', 'bs': 'bs', 'bg': 'bg', 'ca': 'ca',
        'ceb': 'ceb', 'zh': 'zh-CN', 'zh-TW': 'zh-TW', 'co': 'co', 'hr': 'hr',
        'cs': 'cs', 'da': 'da', 'nl': 'nl', 'en': 'en', 'eo': 'eo', 'et': 'et',
        'fi': 'fi', 'fr': 'fr', 'fy': 'fy', 'gl': 'gl', 'ka': 'ka', 'de': 'de',
        'el': 'el', 'gu': 'gu', 'ht': 'ht', 'ha': 'ha', 'haw': 'haw', 'he': 'he',
        'hi': 'hi', 'hmn': 'hmn', 'hu': 'hu', 'is': 'is', 'ig': 'ig', 'id': 'id',
        'ga': 'ga', 'it': 'it', 'ja': 'ja', 'jv': 'jv', 'kn': 'kn', 'kk': 'kk',
        'km': 'km', 'rw': 'rw', 'ko': 'ko', 'ku': 'ku', 'ky': 'ky', 'lo': 'lo',
        'lv': 'lv', 'lt': 'lt', 'lb': 'lb', 'mk': 'mk', 'mg': 'mg', 'ms': 'ms',
        'ml': 'ml', 'mt': 'mt', 'mi': 'mi', 'mr': 'mr', 'mn': 'mn', 'my': 'my',
        'ne': 'ne', 'no': 'no', 'ny': 'ny', 'or': 'or', 'ps': None, 'fa': 'fa',
        'pl': 'pl', 'pt': 'pt', 'pa': 'pa', 'ro': 'ro', 'ru': 'ru', 'sm': 'sm',
        'gd': 'gd', 'sr': 'sr', 'sn': 'sn', 'sd': 'sd', 'si': 'si', 'sk': 'sk',
        'sl': 'sl', 'so': 'so', 'st': 'st', 'es': 'es', 'su': 'su', 'sw': 'sw',
        'sv': 'sv', 'tl': 'tl', 'tg': 'tg', 'ta': 'ta', 'tt': 'tt', 'te': 'te',
        'th': 'th', 'tr': 'tr', 'tk': 'tk', 'uk': 'uk', 'ur': 'ur', 'ug': 'ug',
        'uz': 'uz', 'vi': 'vi', 'cy': 'cy', 'xh': 'xh', 'yi': 'yi', 'yo': 'yo',
        'zu': 'zu'
    }

    # Check if the target language is supported
    language_code = language_codes.get(target_lang)
    if not language_code:
        return jsonify({
            "error": True,
            "message": f"The language '{target_lang}' is not supported for Text-to-Speech. Please select another language."
        }), 400

    # Google TTS request
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
        )

        audio_content = base64.b64encode(response.audio_content).decode("utf-8")
        return jsonify({"audioContent": audio_content})

    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
