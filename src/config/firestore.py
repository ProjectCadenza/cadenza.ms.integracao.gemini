import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred, {
    'storageBucket': 'cadenza-prd-350mt.firebasestorage.app' 
})

firestore_db = firestore.client(database_id="cadenza-apps-prd")
bucket = storage.bucket()
