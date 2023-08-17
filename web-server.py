from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_DIR = "data/parsed"

all_data = []

for file in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, file)
    print(path)

    # Load the JSON data from the file
    with open(path, 'r') as json_file:
        data: list = json.load(json_file)
        all_data.extend(data)

all_data.sort(key=lambda e: e["num"])
print(len(all_data))

@app.route('/')
def index():
    return render_template('index.html', entries=all_data)

@app.route('/data')
def filter_entries():
    return jsonify(all_data)

if __name__ == '__main__':
    app.run(debug=True)
