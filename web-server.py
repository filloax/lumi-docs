from flask import Flask, render_template, request, jsonify
import json
import os
import webbrowser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--open-in-browser", action='store_true')
parser.add_argument("--debug", action='store_true')

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

@app.route('/')
def index():
    return render_template('index.html', entries=all_data)

@app.route('/data')
def data():
    return jsonify(all_data)

@app.route('/data/<num>/<name>')
@app.route('/data/<num>/<name>/<regionOrForm>')
def data_single(num: str, name: str, regionOrForm=None):
    return jsonify(get(num, name, regionOrForm))

@app.route('/details/<num>/<name>')
@app.route('/details/<num>/<name>/<regionOrForm>')
def details(num: str, name: str, regionOrForm=None):
    return render_template('details.html', pokemon=get(num, name, regionOrForm))

def get(num: str, name: str, regionOrForm=None):
    for entry in all_data:
        if str(entry['num']) == num and entry['name'].lower() == name.lower():
            form = entry.get('form', '').lower()
            region = entry.get('region', '').lower()
            if regionOrForm is None or regionOrForm.lower() == form or regionOrForm.lower() == region:
                return entry

    return None

if __name__ == '__main__':
    args = parser.parse_args()

    if args.open_in_browser:
        webbrowser.open('http://localhost:5000')

    app.run(debug=args.debug)
