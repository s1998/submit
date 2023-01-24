
notebooks caontains the cpde used for obtaining the models

Run following commands:

pip install transformers allennlp spacy
python spacy -m download en_core_web_sm

See the following file : requirementsNew.txt


About files in notebooks:
  notebooks/sailesaichalleng.py
    This file uses BART in zero-shot fashion to divide sentences into questions and statements.
    We obtain the files questions.csv and statements.csv .
    
    Then the top samples (250 from each file) of the files are labelled manually.
    This helps in fixing errors + filtering out the filter questions.
    This finally creates two labelled datasets : questions_lablled.csv and statements_labelled.csv

  notebooks/salesaichallenge2.py
    This notebook uses the files questions_lablled.csv and statements_labelled.csv to create a model that is
    used in the final API endpoint and seems to work decently well.

  notebooks/newsalesaichallenge3.py
    There are two steps here. 
    First figure out if the sentence mentions a taks and when is it supposed to be done.
    This can be done using Semnatic Role Labelling.
    Once we have figured out the sentences that have a verb and a time period, 
    we use BART in zero-shot fashion to check if the task is to be done after meeting.
    This creates a file srlTimeV3.csv
    
    The top samples from this file are also labelled, which creates srlTimeV3labelled.csv

  notebooks/newsalesaichallenge4.py
    Using the samples from  srlTimeV3labelled.csv, we create a second classifier that is used for the task of detecting statements that could be potential next steps after the meeting.


Models from notebook 2 and 4 are used in the final deployed API.

The second task is significantly harder (to annotate as well as model).

  

































Previous documentation of the flask app here : 

# Flask API Hugging Face [facebook/bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli)
:hugs: Flask API for Hugging Face's `facebook/bart-large-mnli` model

## Setup

Create a Python virtual environment `py3env`
```
python3 -m venv py3env
```

Activate the virtual environment `py3env`
```
source py3env/bin/activate
```

Install the Python packages from `requirements.txt`
```
pip3 install -r requirements.txt
```

Install PyTorch
```
pip3 install torch==1.9.0+cpu torchvision==0.10.0+cpu torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
```

Run the Flask application `app.py`
```
flask run --host=0.0.0.0
```

## Usage

### Request
Send JSON POST requests to `http://<address>:5000`
```json
{
  "sentence": "Last week I upgraded my iOS version and ever since then my phone has been overheating whenever I use your app.",
  "labels": ["mobile", "website", "billing", "account access"],
  "multi_label": 1
}
```

### Response
```json
{
  "labels": [
    "mobile",
    "account access",
    "billing",
    "website"
  ],
  "scores": [
    0.990887463092804,
    0.4456685483455658,
    0.37061989307403564,
    0.0016618024092167616
  ],
  "sequence": "Last week I upgraded my iOS version and ever since then my phone has been overheating whenever I use your app."
}
```


## Authors

* **Rajat Dipta Biswas** - *Initial work*

See also the list of [contributors](https://github.com/rajatdiptabiswas/flask-api-hugging-face-fb-bart-large-mnli/graphs/contributors) who participated in this project.

## Acknowledgments

* [Hugging Face](https://huggingface.co/)
* [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
