import os
from google.cloud import storage, firestore


def upload_audio_to_gcs(file, destination_blob_name):
    # Inicialización
    storage_client = storage.Client()
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file, rewind=True)
    blob.make_public()  # Si quieres que sea accesible públicamente
    return blob.public_url

def save_metadata_to_firestore(data: dict):
    # Inicialización
    firestore_client = firestore.Client()
    doc_ref = firestore_client.collection("audios").document()
    doc_ref.set(data)
    return doc_ref.id
