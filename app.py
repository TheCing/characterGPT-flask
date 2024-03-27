from flask import Flask, render_template, jsonify, request
from openai import OpenAI
from elevenlabs import generate, play, set_api_key
import speech_recognition as sr
import yaml
from datetime import datetime
from flask_assets import Environment, Bundle

# OpenAI API key
client = OpenAI(api_key="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")

# ElevenLabs API key
elevenlabs_api_key = "ae115be99b6efed5da337213e0a55617"
set_api_key("ae115be99b6efed5da337213e0a55617")

app = Flask(__name__)

# Initialize Flask-Assets
assets = Environment(app)

# Define your SCSS asset bundle
scss_bundle = Bundle(
    'scss/styles.scss',  # Path to your SCSS file (inside the 'static' folder)
    filters='libsass',  # Use the libsass filter for compilation
    output='css/compiled_styles.css',  # Output path for the compiled CSS file (inside the 'static' folder)
    depends=('scss/**/*.scss')  # Optional: Makes sure all SCSS files are recompiled if any one of them changes
)

# Register your asset bundle(s) with Flask-Assets
assets.register('scss_all', scss_bundle)

# Ensure the 'static' folder is correctly set if your static files are in a different location
assets.directory = app.static_folder
assets.url = app.static_url_path

context = []
char_selected = ""
char_index = ""


def generate_completion(message):
    request = message
    context.append({"role": "user", "content": request})
    chat_completion = client.chat.completions.create(model="gpt-3.5-turbo",
                                                     messages=context)
    # chat_completion = client.chat.completions.create(model="gpt-4",
    #                                                  messages=context)
    response = chat_completion.choices[0].message.content
    print(response)
    context.append({"role": "assistant", "content": response})
    return response


def generate_audio(message, voice):
    audio = generate(
        text=message,
        voice=voice,
        model="eleven_monolingual_v1"
    )

    play(audio)
    

@app.route('/post_message', methods=['POST'])
def post_message():
    data = request.json  # Get JSON data sent with the POST request
    input_text = data.get('message', 'No text provided')  # Extract the input text or use a default
    
    print(input_text)
    
    # Generate completion
    completion = generate_completion(input_text)
    print(completion)
    
    # Return the received text (or default message) and completion
    return jsonify({"updatedText": input_text, "completion": completion})


class CharacterManager():
    def __init__(self):
        self.voice = None
        self.characters = []
        self.current_rules = None
        self.current_char = None
        self.log = None
        self.data = None
        self.init()

    def init(self):
        # self.load_rules()
        
        self.load_character_list()
        
        self.set_rules(0)

        self.build_character_select()

        self.log = []  # List to store submitted inputs

    # Load character rules from rules file
    def load_rules(self):
        try:
            with open("rules-dm.txt", "r") as file:
                self.log = [line.strip() for line in file]
                context.extend([{"role": "system", "content": line} for line in self.log])
                # print(context)
        except FileNotFoundError:
            print("No rules.txt file found.")

    def load_character_list(self):
        try:
            # Read YAML data from a file
            with open('characters.yaml', 'r') as file:
                self.data = yaml.load(file, Loader=yaml.FullLoader)
                # print(self.data)

                # Iterate through each character in the TOML data
                for character in self.data['character']:
                    # Create a dictionary for each character with their name and rules
                    character_info = {
                        'name': character['name'],
                        'voice': character['voice'],
                        'rules': character['rules']
                    }
                    # Append the character dictionary to the characters list
                    self.characters.append(character_info)

                # Now, characters is an array of dictionaries, each containing the name and rules for a character
                # print(self.characters)
                
        except FileNotFoundError:
            print("No characters.yaml file found.")

    def load_character(self):
        # print(f'Current index: {self.character_select.currentIndex()}')
        # print(f'Current text: {self.character_select.currentText()}')
        selected_char = 0
        self.set_rules(selected_char)

    def set_rules(self, selected_char):
        self.current_char = self.characters[selected_char]['name']
        self.current_voice = self.characters[selected_char]['voice']
        self.current_rules = self.characters[selected_char]['rules']
        print(f'Current character: {self.current_char}')
        print(f'Current voice: {self.current_voice}')
        print(f'Current rules: {self.current_rules}')
        self.voice = self.current_voice
        self.log = [line.strip() for line in self.characters[selected_char]['rules']]
        context.clear()
        context.extend([{"role": "system", "content": line} for line in self.log])
        # print(f'Current context: {context}')

    def build_character_select(self):
        # self.character_select.setPlaceholderText(self.characters[0]['name'])
        # self.character_select.addItem("TEST")
        # for character in self.characters:
            # self.character_select.addItem(character['name'])
            # print(character['name'])
        return

charMan = CharacterManager()

@app.route('/')
def home():
    currentChar = charMan.current_char
    return render_template('index.html', current_char=currentChar)

if __name__ == "__main__":
    audio_enabled = False  # adjust to enable TTS
    charMan.init()
    app.run(debug=True)