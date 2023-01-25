from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import List
from flask import Flask, request, jsonify
import re
import torch
import numpy as np
from tqdm.notebook import tqdm
import os, re

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

questions_model = AutoModelForSequenceClassification.from_pretrained(
    './questions_model/').to(device)
new_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

followup_model = AutoModelForSequenceClassification.from_pretrained(
    './followup_model/').to(device)
new_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

def get_prediction(text):
    encoding = new_tokenizer(text, return_tensors="pt", 
        padding="max_length", truncation=True, max_length=128)
    encoding = {k: v.to(questions_model.device) for k,v in encoding.items()}

    outputs = questions_model(**encoding)
    logits = outputs.logits

    sigmoid = torch.nn.Softmax(dim=-1)
    probs = sigmoid(logits.squeeze().cpu())
    probs = probs.detach().numpy()
    label = np.argmax(probs, axis=-1)
    
    if label == 1:
        return ('question', probs[1])
    else:
        return ('statement', probs[0])

def get_prediction_followup(text):
    encoding = new_tokenizer(text, return_tensors="pt", 
        padding="max_length", truncation=True, max_length=128)
    encoding = {k: v.to(questions_model.device) for k,v in encoding.items()}

    outputs = followup_model(**encoding)
    logits = outputs.logits

    sigmoid = torch.nn.Softmax(dim=-1)
    probs = sigmoid(logits.squeeze().cpu())
    probs = probs.detach().numpy()
    label = np.argmax(probs, axis=-1)
    
    if label == 1:
        return ('followup', probs[1])
    else:
        return ('negative', probs[0])

# flask server
app = Flask(__name__)

import spacy
nlp = spacy.load('en_core_web_sm') # Load the English Model


from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging

predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz",
                                cuda_device=0)


def get_questions(text):
    print("Here ****** ", text)
    all_sents = []

    for l in text:
        l = l.strip()
        if l.startswith("Client"):
            l = re.sub("Client [0-9]*:","", l,count=1)
            doc = nlp(l)
            for sent in doc.sents:
                all_sents.append(("client", str(sent)))
        else:
            l = " ".join(l.split(":")[1:])
            doc = nlp(l)
            for sent in doc.sents:
                all_sents.append(("host", str(sent)))

    prediction_list = []    
    for i, (speaker, sent) in enumerate(all_sents):
        if speaker == "host":
            continue

        ans = get_prediction(sent)
        print(sent, ans)

        if ans[0] == "question":
            prediction_list.append((ans, sent, all_sents[i-5:i+5]))

    return prediction_list

def get_future_work(text, debug=False):
    
    all_sents = []

    for l in text:
        l = l.strip()
        l = " ".join(l.split(":")[1:])
        doc = nlp(l)
        for sent in doc.sents:
            all_sents.append(str(sent))
    
    # included_sents = []
    # for i, sent in enumerate(all_sents):
    #     kk = predictor.predict(sentence=sent)
    #     verbs = kk['verbs']

    #     times = []
    #     vbs_lst = []
    #     for verb in verbs:
    #         include = False
    #         for t in verb['tags']:
    #             if 'tmp' in t.lower():
    #                 include = True

    #         if include:
    #             times.append([x for x, y in zip(kk['words'], verb['tags']) if 'tmp' in y.lower()])
    #             vbs_lst.append(verb["verb"])

    # if len(times):
    #     included_sents.append((times, vbs_lst, sent, all_sents[i-5:i+5]))

    # prediction_list = []    
    # for i, (times, vbs_lst, sent, context) in enumerate(included_sents):
    #     ans = get_prediction_followup(sent)
    #     print(sent, ans)

    #     if ans[0] == "followup":
    #         prediction_list.append((ans, sent, context))

    prediction_list = []    
    for i, sent in enumerate(all_sents):
        ans = get_prediction_followup(sent)
        if debug:
            print(sent, ans)

        if ans[0] == "followup":
            prediction_list.append((ans, sent, all_sents[i-5:i+5]))

    prediction_list = sorted(prediction_list, key=lambda x : x[0][1])
    for tt in prediction_list[-100:]:
        print(tt)
    
    included_sents = []
    for i, (ans, sent, context) in enumerate(prediction_list[-100:]):
        kk = predictor.predict(sentence=sent)
        print(ans, sent, context)
        print("\t", kk['verbs'])
        verbs = kk['verbs']

        times = []
        vbs_lst = []
        for verb in verbs:
            include = False
            for t in verb['tags']:
                if 'tmp' in t.lower():
                    include = True

            if include:
                times.append([x for x, y in zip(kk['words'], verb['tags']) if 'tmp' in y.lower()])
                vbs_lst.append(verb["verb"])
        
        print("\t\tinclude : ", len(times))

        if len(times):
            included_sents.append((ans, sent, context))

    for _, sent, _ in included_sents:
        print(sent)

    return included_sents

# define flash routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.json



        if data is None:
            return jsonify({"error": "Invalid JSON request"})
        elif not ("sentence" in data and "labels" in data):
            print(data)
            text = [t.strip() for t in data["text"].split("\n") if t.strip()]

            print("Printing questions ..... ")
            questions = get_questions(text)
            questions = sorted(questions, key=lambda x: x[0][1])
            for ans, question, context in questions:
                print("\n\t", ans)
                print("\t", question)
                for t in context:
                    print("\t\t", t)

            print("Printing future work ..... ")
            followup = get_future_work(text, True)
            followup = sorted(followup, key=lambda x: x[0][1])
            for ans, task, context in followup:
                print("\n\t", ans)
                print("\t", task)
                for t in context:
                    print("\t\t", t)

            selected_followup =  [(t[1], t[2]) for t in  followup if t[0][1] > 0.6]
            if not selected_followup:
                selected_followup = [(t[1], t[2]) for t in  followup[-3:]]

            selected_followup = [{"followup" : t[0], "context" : t[1]} for t in selected_followup]

            return jsonify(
                {
                    "question" : [{"question" : t[1], "context" : t[2]} for t in questions if t[0][1] > 0.8],
                    "followup" : selected_followup
                }
            )
        elif not (
            isinstance(data["sentence"], str)
            and isinstance(data["labels"], list)
        ):
            return jsonify(
                {
                    "error": "'sentence' field is not a string and/or 'labels' field is not a list of strings"
                }
            )
        elif "multi_label" in data and not (isinstance(data["multi_label"], int)):
            return jsonify(
                {
                    "error": "'multi_label' field is not an integer"
                }
            )

        try:
            if ("multi_label" in data):
                result = classify(data["sentence"], data["labels"], data["multi_label"])
            else:
                result = classify(data["sentence"], data["labels"])
            return jsonify(result)
        except Exception as exception:
            return jsonify({"error": str(exception)})

    return """<h1>Flask Server Running</h1>
        <p>
            Send a JSON POST request in the format
            {
                "sentence": "...",
                "labels": ["...", "...", "..."]
                "multi_label": 0 / 1
            }
            to get predictions
        </p>"""


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5000)

