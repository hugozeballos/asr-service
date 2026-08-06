import os
from google.cloud import storage, firestore


def upload_audio_to_gcs(file, destination_blob_name):
    """Uploads a file to the GCS_BUCKET_NAME bucket and returns its public URL.

    The blob is made public so the saved URL can be played back directly by
    the frontend's <audio> element without a signed-URL/proxy step.
    """
    storage_client = storage.Client()
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file, rewind=True)
    blob.make_public()
    return blob.public_url

def save_metadata_to_firestore(data: dict):
    """Stores a transcription/correction record in the "audios" Firestore collection."""
    firestore_client = firestore.Client()
    doc_ref = firestore_client.collection("audios").document()
    doc_ref.set(data)
    return doc_ref.id
