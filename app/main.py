import logging
import os
from datetime import datetime

import google.cloud.logging
from flask import Flask, render_template, request
from google.cloud import firestore
from google.cloud import language_v1 as language
from google.cloud import storage
from google.cloud import translate_v2 as translate

client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def root():
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    successful_upload = False
    if request.method == 'POST':
        uploaded_file = request.files.get('picture')

        if uploaded_file:
            gcs = storage.Client()
            bucket = gcs.get_bucket(os.environ.get('BUCKET', 'my-bmd-bucket'))
            blob = bucket.blob(uploaded_file.filename)

            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )

            logging.info(blob.public_url)

            successful_upload = True

    return render_template('upload_photo.html',
                           successful_upload=successful_upload)


@app.route('/search')
def search():
    query = request.args.get('q')
    results = []

    if query:
        queries = translate_query(query)
        # if the input is a phrase
        if len(query.split(" ")) > 1:
            queries += get_important_words_from_phrase(queries)

        doc = get_collections(queries)

        try:
            for url in doc['photo_urls']:
                results.append(url)
            results = list(dict.fromkeys(results))
        except TypeError as _e:
            pass
        except KeyError as _e:
            pass
    return render_template('search.html', query=query, results=results)


def get_collections(queries):
    db = firestore.Client()
    all_docs = {}
    for query in queries:
        doc = db.collection(u'tags').document(query.lower()).get().to_dict()
        if doc is not None:
            all_docs = {**all_docs, **doc}

    return all_docs


def get_important_words_from_phrase(queries):
    all_kw = []
    lang_client = language.LanguageServiceClient()
    for query in queries:
        type_ = language.Document.Type.PLAIN_TEXT
        document = {"content": query, "type_": type_}
        encoding_type = language.EncodingType.UTF8
        all_kw += get_entities(lang_client, document, encoding_type)
        all_kw += get_keywords(lang_client, document, encoding_type)

    return all_kw


def get_entities(lang_client, document, encoding_type):
    entities = []
    response = lang_client.analyze_entities(document=document, encoding_type=encoding_type)
    for entity in response.entities:
        entities.append(entity.name)
        if language.Entity.Type(entity.type_).name != "OTHER":
            entities.append(language.Entity.Type(entity.type_).name)
    return entities


def get_keywords(lang_client, document, encoding_type):
    entities = []
    response = lang_client.analyze_syntax(document=document, encoding_type=encoding_type)
    for token in response.tokens:
        part_of_speech = language.PartOfSpeech.Tag(token.part_of_speech.tag).name
        if part_of_speech == "NOUN":
            entities.append(token.text.content)
    return entities


def translate_query(query):
    queries = [query]
    translate_client = translate.Client()
    lang = translate_client.detect_language(query)["language"]

    if lang != "en":
        queries.append(translate_client.translate(query, target_language="en")['translatedText'])

    return queries


@app.errorhandler(500)
def server_error(_e):
    logging.exception('An error occurred during a request.')
    return render_template('error.html', error=500), 500


@app.errorhandler(404)
def page_not_found(_e):
    logging.exception('An error occurred during a request.')
    return render_template('error.html', error=404), 404


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
