from __future__ import unicode_literals, print_function
from flask import Flask, request, jsonify
import requests

import io
import json
from snips_nlu import SnipsNLUEngine
import logging
from snips_nlu.default_configs import CONFIG_EN
from multiprocessing import Process, Queue
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

app = Flask(__name__)

# def generate_to_do_list(parsed):
#     intent = [parsed['intent']['intentName']]
#     slots = parsed['slots']
#     for slot in slots:
#         intent.append(slot['rawValue'])
#     return ' '.join(intent)

def accumulate_json_objects(objs):
    accumulated_data = {
        "input": [],
        "intent": {
            "intentName": [],
            "probability": []
        },
        "slots": []
    }

    for obj in objs:
        accumulated_data["input"].append(obj["input"])
        accumulated_data["intent"]["intentName"].append(obj["intent"]["intentName"])
        accumulated_data["intent"]["probability"].append(obj["intent"]["probability"])
        accumulated_data["slots"].extend(obj["slots"])

    return accumulated_data

def snips_nlu_model(data, snips_queue: Queue):
    with io.open("sales_dataset.json") as f:
        sample_dataset = json.load(f)
    nlu_engine = SnipsNLUEngine(config=CONFIG_EN)
    nlu_engine = nlu_engine.fit(sample_dataset)
    sentences = data.split('. ')

    # Add period back to each sentence (optional, depending on your needs)
    sentences = [sentence + '.' for sentence in sentences]
    parsed_list = []
    for sentence in sentences:
        print(sentence)
        parsed = nlu_engine.parse(sentence)
        parsed_list.append(parsed)
    parsing = accumulate_json_objects(parsed_list)
    result = parsing['intent']['intentName']
    print(result)
    print("slots:",parsing["slots"])
    filtered_list = [item for item in result if item is not None]

    # Remove duplicates
    unique_list = list(set(filtered_list))
    joined_string = ' \n'.join(unique_list)
    snips_queue.put(joined_string)
    print("Snips-nlu completed")


def separate_speakers(text: str):
    parts = text.split("SPEAKER_")
    # Filter out any empty parts that may result from the split
    parts = [part for part in parts if part]

    # Initialize empty strings for each speaker
    speaker_01 = "" # String for customer
    speaker_00 = "" # String for sales person

    # Iterate over the parts to assign them to the respective speaker strings
    for part in parts:
        if part.startswith("01:"):
            speaker_01 += part[3:].strip() + " "
        elif part.startswith("00:"):
            speaker_00 += part[3:].strip() + " "

    # Strip any trailing spaces
    speaker_01 = speaker_01.strip()
    speaker_00 = speaker_00.strip()
    return speaker_01,speaker_00


def sentiment_analysis(text, sentiment_queue: Queue):
    tokenizer = AutoTokenizer.from_pretrained("SchuylerH/bert-multilingual-go-emtions")
    model = AutoModelForSequenceClassification.from_pretrained("SchuylerH/bert-multilingual-go-emtions")
    nlp = pipeline("sentiment-analysis", model = model, tokenizer = tokenizer)
    customer_text, sales_text = separate_speakers(text)
    # print("customer text", customer_text)
    # print("sales text", sales_text)
    customer_result = nlp(customer_text)
    sales_result = nlp(sales_text)
    # print("customer sentiment:",customer_result)
    # print("sales sentiment:", sales_result)
    joined_customer = [item['label'] for item in customer_result]
    customer_str = ', '.join(joined_customer)
    joined_sales = [item['label'] for item in sales_result]
    sales_str = ', '.join(joined_sales)
    print("sentiment analysis completed")
    sentiment_queue.put({"customer sentiment":customer_str,"sales sentiment":sales_str})

@app.route('/transcription', methods=['POST'])
def process_A():
    snips_queue = Queue()
    sentiment_queue = Queue()
    data = request.json
    transcription = data.get('transcription')
    if not transcription:
        return jsonify({'error': 'No transcription data received'}), 400
    print("Received transcription:", transcription)

    snips_process = Process(target=snips_nlu_model, args=(transcription,snips_queue,))
    sentiment_process = Process(target=sentiment_analysis, args=(transcription,sentiment_queue,))

    snips_process.start()
    sentiment_process.start()

    snips_process.join()
    sentiment_process.join()

    todos = snips_queue.get()
    sentiments = sentiment_queue.get()
    
    print("text processed")
    data = {'message': 'Processed data', 'processed_data': 
            {'transcription':transcription,'todos':todos, 'customer sentiment':sentiments['customer sentiment'], 
             'sales sentiment':sentiments['sales sentiment']}}
    return jsonify(data), 200


if __name__ == '__main__':
    app.run(port=5001,debug=True)
