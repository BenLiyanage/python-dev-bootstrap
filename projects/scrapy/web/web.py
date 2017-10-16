import json

from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py


@app.route('/')
@app.route('/<selected_drug>')
@app.route('/<selected_drug>/<format>')
def index(selected_drug=None, format='html'):
    drugs = []
    drug_info = selected_drug
    print(format)
    for path, directory, filenames in os.walk("../drugscraper/data"):
        # import pdb
        # pdb.set_trace()
        if 'data.json' in filenames:
            # Last item in the folder name is the name of the drug.
            drug_folder = path.split('/')[-1]
            drug_text = drug_folder.replace('-', ' ')
            drugs.append(
                {
                    'folder': drug_folder,
                    'text': drug_text,
                }
            )

            if selected_drug == None:
                selected_drug = drug_folder

            if selected_drug == drug_folder:
                with open(path + '/data.json') as data:
                    drug_info = json.load(data)
    if format == 'json':
        return jsonify(drug_info)
    else:
        return render_template('list.html', drugs=drugs, drug_info=drug_info, selected_drug=selected_drug)

