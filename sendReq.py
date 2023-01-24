import json
import pprint
import requests

url = 'http://0.0.0.0:5000/'

fname = "transcripts/63a310f9a39c8c8e9c40cb6f.txt"
fname = "transcripts/63a1f0b4a39c8c8e9c2b469c.txt"

fnames = ["6378020532887928c06794c4.txt",
"6386352ca39c8c8e9c08f6c3.txt",
"638f671ca39c8c8e9cc7670e.txt",
"63b5a912a39c8c8e9c9c73b2.txt",
"637812a932887928c068d817.txt",
"638639dca39c8c8e9c09579b.txt",
"63869634a39c8c8e9c10d6ee.txt",
"638f6b57a39c8c8e9cc7c59c.txt",]

fnames = ["63853b9aa39c8c8e9cf4e388.txt",
"638e4a3ca39c8c8e9cafeed1.txt",
"6398e26ea39c8c8e9c7ff842.txt",
"639cb1b9a39c8c8e9cc8b15a.txt",
"63b48a27a39c8c8e9c864e1a.txt",
"638540b8a39c8c8e9cf54df8.txt",
"638e704aa39c8c8e9cb31b7e.txt",
"6398e851a39c8c8e9c806e12.txt",
"639cb8b7a39c8c8e9cc94db7.txt",
"63b48a2aa39c8c8e9c866126.txt",
"638619d0a39c8c8e9c06c163.txt",
"638e7898a39c8c8e9cb3cb92.txt",
"63990ba1a39c8c8e9c833677.txt",
"639cc00ea39c8c8e9cc9ea3c.txt",
"63b48a2da39c8c8e9c867e9e.txt",
"63862794a39c8c8e9c07de39.txt",
"638ea3dca39c8c8e9cb7665a.txt",
"6399e273a39c8c8e9c92c76b.txt",
"639cdfeba39c8c8e9ccc830e.txt",
]

for fname in fnames:
    print("\n\n\n\n\n\n")
    print("Working with file ....... {}".format(fname))
    with open("transcripts/" + fname, "r") as f:
        sents = f.readlines()
        sents = [l.strip() for l in sents if l.strip()]

    myobj = {"text": "\n".join(sents)}

    x = requests.post(url, json = myobj)

    # print(x.text)
    text = json.loads(x.text)
    for k in text:
        print(k)
        for sent, context in text[k]:
            print("\t", sent)
            for c in context:
                print("\t\t", c)
    # (json.dumps(x.text, indent=1))