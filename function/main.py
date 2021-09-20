import os

from google.cloud import firestore
from google.cloud import vision


def photo_analysis_service(event, context):
    bucket = os.environ.get('BUCKET', 'my-bmd-bucket')
    file_name = event['name']

    tags = _analyze_photo(bucket, file_name)
    _store_results(bucket, file_name, tags)


def _analyze_photo(bucket, file_name):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(source=vision.ImageSource(image_uri=f'gs://{bucket}/{file_name}'))
    tags = _get_all_labels(client, image)

    return tags


def _get_all_labels(client, image):
    # get Objects
    objects = client.object_localization(image=image).localized_object_annotations
    print(objects)
    # get Label
    labels = client.label_detection(image=image).label_annotations
    print(labels)
    # get Logos
    logos = client.logo_detection(image=image).logo_annotations
    print(logos)
    # get Landmarks
    places = client.landmark_detection(image=image).landmark_annotations
    print(places)
    # get bestGuessLabels
    annotations = client.web_detection(image=image).web_detection.best_guess_labels
    print(annotations)
    # get text
    texts = client.text_detection(image=image).text_annotations
    print(texts)
    hand_write = client.document_text_detection(image=image).text_annotations

    # merge all labels
    tags = []
    tags += map(lambda object_: object_.name.lower(), objects)
    tags += map(lambda label: label.description.lower(), labels)
    tags += map(lambda logo: logo.description.lower(), logos)
    tags += map(lambda place: place.description.lower(), places)
    tags += map(lambda annotation: annotation.label.lower(), annotations)
    tags += map(lambda text: text.description.lower(), texts)
    tags += map(lambda text: text.description.lower(), hand_write)

    return tags


def _store_results(bucket, file_name, tags):
    db = firestore.Client()

    for tag in tags:
        db.collection(u'tags').document(tag).set(
            {u'photo_urls': firestore.ArrayUnion(
                [u'https://storage.googleapis.com/{}/{}'.format(bucket, file_name)]
            )
            },
            merge=True)

        print('\nThe picture is {} a {}'.format(file_name, tag))
