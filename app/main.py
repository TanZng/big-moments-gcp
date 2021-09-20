import logging
import os

from flask import Flask, render_template, request
import google.cloud.logging
from google.cloud import firestore
from google.cloud import storage
from google.cloud import translate_v2 as translate

client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()

app = Flask(__name__)


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
        db = firestore.Client()
        original_doc = db.collection(u'tags').document(query.lower()).get().to_dict()
        if original_doc is None:
            original_doc = {}

        doc_en = translate_query(query, db)
        if doc_en is None:
            doc_en = {}

        try:
            doc = {**original_doc, **doc_en}
            for url in doc['photo_urls']:
                results.append(url)
                results = list(dict.fromkeys(results))
        except TypeError as e:
            pass
        except KeyError as e:
            pass
    return render_template('search.html', query=query, results=results)


def translate_query(query, db):
    doc_en = {}
    translate_client = translate.Client()
    result = translate_client.detect_language(query)["language"]

    if result != "en":
        en_query = translate_client.translate(query, target_language="en")['translatedText']
        doc_en = db.collection(u'tags').document(en_query.lower()).get().to_dict()

    return doc_en


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return render_template('error.html', error=500), 500


@app.errorhandler(404)
def page_not_found(e):
    logging.exception('An error occurred during a request.')
    return render_template('error.html', error=404), 404


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
