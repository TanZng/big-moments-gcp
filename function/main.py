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

    print(f"Tags: {tags} \nfor Image: gs://{bucket}/{file_name}")

    return tags


def _get_all_labels(client, image):
    # get Objects
    objects = client.object_localization(image=image).localized_object_annotations
    # get Label
    labels = client.label_detection(image=image).label_annotations
    # get Logos
    logos = client.logo_detection(image=image).logo_annotations
    # get Landmarks
    places = client.landmark_detection(image=image).landmark_annotations
    # get bestGuessLabels
    annotations = client.web_detection(image=image).web_detection.best_guess_labels
    # get text
    texts = client.text_detection(image=image).text_annotations
    hand_write = client.document_text_detection(image=image).text_annotations
    # get mood
    likelihoods = get_likelihood(client, image)

    # merge all labels
    tags = []
    tags += map(lambda object_: object_.name.lower(), objects)
    tags += map(lambda label: label.description.lower(), labels)
    tags += map(lambda logo: logo.description.lower(), logos)
    tags += map(lambda place: place.description.lower(), places)
    tags += map(lambda annotation: annotation.label.lower(), annotations)
    tags += map(lambda text: text.description.lower(), texts)
    tags += map(lambda text: text.description.lower(), hand_write)
    tags += map(lambda likelihood: likelihood.lower(), likelihoods)

    # remove duplicate
    tags = list(dict.fromkeys(tags))
    return tags


def get_likelihood(client, image):
    response = client.face_detection(image=image)
    faces = response.face_annotations

    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')

    likelihoods = []
    person_count = 0

    for face in faces:
        person_count += 1
        likelihoods.append('person')

        if likelihood_name[face.anger_likelihood] in ('LIKELY', 'VERY_LIKELY'):
            likelihoods.extend(['anger', 'angry'])

        if likelihood_name[face.joy_likelihood] in ('LIKELY', 'VERY_LIKELY'):
            likelihoods.extend(['happy', 'smile', 'joy'])

        if likelihood_name[face.sorrow_likelihood] in ('LIKELY', 'VERY_LIKELY'):
            likelihoods.extend(['sorrow', 'sad', 'cry'])

        if likelihood_name[face.surprise_likelihood] in ('LIKELY', 'VERY_LIKELY'):
            likelihoods.extend(['surprise', 'surprised person'])

    if person_count == 1:
        likelihoods.append(f"person")
    elif person_count > 1:
        likelihoods.extend([f"{person_count} people", "people"])

    return likelihoods


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
