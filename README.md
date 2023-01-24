
## Submission

- [Installation](#installation)
- [Code](#code)
- [Discussion](#discussion)
- [Server](#server)

### Installation



Run following commands:

pip install transformers allennlp spacy

python spacy -m download en_core_web_sm

See the following file (for versions of the library) : requirementsNew.txt

### Code

Notebooks folder contains the code used for obtaining the models.

(These were actually colab notebooks that have been download as python file, let me know if actual notebooks are needed).

About files in notebooks:

-   notebooks/sailesaichalleng.py

    This file uses (NLI trained) BART in zero-shot fashion to divide sentences into questions and statements.
    We obtain the files questions.csv and statements.csv .

    Then the top samples of the files (250 from each) are labelled manually.
    This helps in fixing errors + filtering out the filler questions.
    This finally creates two labelled datasets : questions_lablled.csv and statements_labelled.csv

-    notebooks/salesaichallenge2.py

     This notebook uses the files questions_lablled.csv and statements_labelled.csv to create a model that is used in the final API endpoint and seems to work decently well.  

-   notebooks/newsalesaichallenge3.py

    There are two steps here. 
    First figure out if the sentence mentions a taks and when is it supposed to be done (this is an important criteria for filtering but we should be able to do without it in next iteration for example with better labelling budget or more carefully tuned zero-shot model + prompts).
    This can be done using Semnatic Role Labelling.
    Once we have figured out the sentences that have a verb and a time period, we use (NLI trained) BART in zero-shot fashion to check if the task is to be done in future.
    This creates a file srlTimeV3.csv

    The top samples from this file are also labelled, which creates srlTimeV3labelled.csv .

-   notebooks/newsalesaichallenge4.py

    Using the samples from  srlTimeV3labelled.csv, we create a second classifier that is used for the task of detecting statements that could be potential next steps after the meeting.


Models from notebook 2 and 4 are used in the final deployed API.

The second task is significantly harder (to annotate as well as model).

### Discussion

Regarding the model size:


Regarding the model performance:



### server

To run the server, use command `python app.py`


A sample use of endpoint is present in the file sendReq.py .


  

































Previous repository of the flask app (based on which the server was created) here : 

https://github.com/rajatdiptabiswas/flask-api-hugging-face-fb-bart-large-mnli

