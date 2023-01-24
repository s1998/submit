# -*- coding: utf-8 -*-
"""newSalesAiChallenge4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SsskeQDl09JM8drthzlWApwV9cXJ4So0
"""

import pandas as pd
df = pd.read_csv('srlTimeV3_labelled.csv')

pos = df[(df.index < 200) & (df['label'] == 1)]['sentence'].tolist()
neg = df[(df.index < 200) & (df['label'] == 0)]['sentence'].tolist() + df[(df.index > 300)].sample(200)['sentence'].tolist()

# !pip install transformers datasets

from transformers import AutoTokenizer
modelname = 'bert-base-uncased'

tokenizer = AutoTokenizer.from_pretrained(modelname)

def process_data(text, labelgiven=0):
    text = ' '.join(text.split())

    encodings = tokenizer(text, padding="max_length", truncation=True, max_length=128)

    encodings['label'] = labelgiven
    encodings['text'] = text

    return encodings

processed_data = []
for neg_ in neg:
  processed_data.append(process_data(neg_, 0))
for pos_ in pos:
  processed_data.append(process_data(pos_, 1))

from sklearn.model_selection import train_test_split
new_df = pd.DataFrame(processed_data)
train_df, valid_df = train_test_split(new_df, test_size=0.2, random_state=2022, stratify=new_df['label'])

import pyarrow as pa
from datasets import Dataset

train_hg = Dataset(pa.Table.from_pandas(train_df))
valid_hg = Dataset(pa.Table.from_pandas(valid_df))

from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

from transformers import AutoModelForSequenceClassification
import torch

model = None
torch.cuda.empty_cache()

model = AutoModelForSequenceClassification.from_pretrained(
    modelname, num_labels=2)

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(output_dir="./result", evaluation_strategy="epoch", num_train_epochs=5, 
                                  warmup_ratio=0.1, learning_rate=0.00001)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_hg,
    eval_dataset=valid_hg,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()
print(trainer.evaluate())
model.save_pretrained('./model_future_work/')



print(trainer.evaluate())



from google.colab import drive
drive.mount('/content/gdrive')

!cp /content/model_future_work/pytorch_model.bin /content/gdrive/My\ Drive



















