# Big Moments
Project for the `Big Moments: Developer Edition GCP Challenge` | #INSIDEGoogleCloud

Big Moments is a Google Photos Clone for the INSIDE Google Cloud '21 Challenge.

Broad improvements:
- [x] Better UI
- [x] Better object detection
- [x] Better CI/CD in GCP
- [x] Custom domain

# 🚀 Features

### Search by the number of people in the picture. ⭐

<img src="https://drive.google.com/uc?export=view&id=1d-tPRt-p4muPa2bEuV2NjzcPSZCcpCTz" data-canonical-src="https://drive.google.com/uc?export=view&id=1d-tPRt-p4muPa2bEuV2NjzcPSZCcpCTz" height="400" />

### Not enough results? What about these suggestions?

<img src="https://drive.google.com/uc?export=view&id=16ojUaTiZ8LnDQNNSz0Ps88pElChFnvkq" data-canonical-src="https://drive.google.com/uc?export=view&id=16ojUaTiZ8LnDQNNSz0Ps88pElChFnvkq" height="400" />

### Identify objects, places, logos, animal breeds, etc.

<img src="https://drive.google.com/uc?export=view&id=1InSgqxATvfIR1G5qOtiQmJwRkRSgeHvQ" data-canonical-src="https://drive.google.com/uc?export=view&id=1InSgqxATvfIR1G5qOtiQmJwRkRSgeHvQ" height="400" />

> The puppy is using an iPad 🐶!

### The typos will not stop you!

<img src="https://drive.google.com/uc?export=view&id=1Dj_rW16v45kbBiQWD4IhwdmvEmBgUT3g" data-canonical-src="https://drive.google.com/uc?export=view&id=1Dj_rW16v45kbBiQWD4IhwdmvEmBgUT3g" height="400" />

### Get results based on memes.

<img src="https://drive.google.com/uc?export=view&id=1699CffBbvfnNK5fWMP6-rtLkAx9r3V-p" data-canonical-src="https://drive.google.com/uc?export=view&id=1699CffBbvfnNK5fWMP6-rtLkAx9r3V-p" height="400" />

### Search by the language you desire.

<img src="https://drive.google.com/uc?export=view&id=1RKtmQvtnPiZTnesguQ6lAD85p1AEV326" data-canonical-src="https://drive.google.com/uc?export=view&id=1RKtmQvtnPiZTnesguQ6lAD85p1AEV326" height="400" />

### Search the image by the text they contain.

<img src="https://drive.google.com/uc?export=view&id=1ah5JT5rRhN_0SekuWogXOxyR49fptEDh" data-canonical-src="https://drive.google.com/uc?export=view&id=1ah5JT5rRhN_0SekuWogXOxyR49fptEDh" height="400" />

# 🏗 Infrastructure

<img src="https://drive.google.com/uc?export=view&id=10QFLSzQ5fnW4rAUARHk0hfKEolE_Zgwq" data-canonical-src="https://drive.google.com/uc?export=view&id=10QFLSzQ5fnW4rAUARHk0hfKEolE_Zgwq" />

# 🏁 Roadmap
- [x] Create a bucket in **Cloud Storage**.
- [x] Create a trigger in **Cloud Build** to build the Docker image on `./app` changes.
  - [x] Save the build image on **Container Registry**.
- [x] Instance a VM with **Compute Engine** for the container imagen.
- [x] Create a repo for the `photo_analysis_service` function in **Cloud Source Repositories**.
- [x] Create a trigger to run **Vision API** tagging.
- [x] Create a DB in **Firestore** to keep the pictures url their related tags.

### 🎉 Extra
- [x] Detect more objects with **Vision AI**.
- [x] Get the number of people in a picture with **Vision AI**.
- [x] Analyze the user query with **Cloud Natural Language**.
  - [x] Suggest results based on the analysis.
- [x] Add multilingual support with **Cloud Translation**.
- [x] Add a custom domain.
  - [x] Add an **HTTPS Load Balancing**.

- [x] Update function from **Cloud Functions**. 
```bash
gcloud functions deploy photo_analysis_service \
       --source=https://source.developers.google.com/projects/project-id/repos/repo-name/moveable-aliases/main/paths/function/ \
       --runtime=python39 --trigger-resource=big-moments-bucket \
       --trigger-event=google.storage.object.finalize \
       --set-env-vars BUCKET=big-moments-bucket
```
- [x] Update container images from **Compute Engine** VM instance. 
```bash
gcloud compute instances update-container instance-name --zone us-central1-a \
       --container-image=gcr.io/project-id/repo@sha256:hash
```
