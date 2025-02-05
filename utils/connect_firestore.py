import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore DB
def init_firestore():
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': os.getenv('GOOGLE_CLOUD_PROJECT'),
        })
    return firestore.client()

# Add data to Firestore
def add_data(collection_name, document_id, data):
    # Initialize Firestore DB
    db = init_firestore()
    db.collection(collection_name).document(document_id).set(data, merge=True)
    print(f'Data added to {collection_name}/{document_id}')

# Get data from Firestore
def get_data(collection_name, document_id):
    db = init_firestore()
    doc = db.collection(collection_name).document(document_id).get()
    if doc.exists:
        print(f'Data from {collection_name}/{document_id}: {doc.to_dict()}')
        return doc.to_dict()
    else:
        print(f'No such document: {collection_name}/{document_id}')
        return None

# Update data in Firestore
def update_data(collection_name, document_id, data):
    db = init_firestore()
    db.collection(collection_name).document(document_id).update(data)
    print(f'Data updated in {collection_name}/{document_id}')

# Get document list from Firestore
def get_document_list(collection_name):
    db = init_firestore()
    docs = db.collection(collection_name).list_documents()
    doc_list = []
    for doc in docs:
        doc_list.append(doc.id)
    print(f'Document list from {collection_name}: {doc_list}')
    return doc_list

# Get the key list in the selected document_id from Firestore
def get_word_list(collection_name, document_id):
    db = init_firestore()
    doc = db.collection(collection_name).document(document_id).get()
    word_list = []
    if doc.exists:
        # Get the key list in the selected document_id
        word_list = list(doc.to_dict().keys())

        print(f'Word list from {collection_name}/{document_id}: {word_list}')
    else:
        print(f'No such document: {collection_name}/{document_id}')
    return word_list

# Delete data from Firestore
def delete_data(collection_name, document_id):
    db = init_firestore()
    db.collection(collection_name).document(document_id).delete()
    print(f'Data deleted from {collection_name}/{document_id}')

# Example usage
if __name__ == "__main__":
    # Add data example
    add_data('users', 'user1', {'name': 'Ryoichi Sato', 'email': 'r.sato@example.com'})

    # Get data example
    user_data = get_data('users', 'user1')

    print(user_data)

    # Update data example
    update_data('users', 'user1', {'email': 'ryoichi.sato@example.com'})

    # Get updated data example
    user_data = get_data('users', 'user1')

    # Add data example
    add_data('users', 'user2', {'name': 'John Doe', 'email': 'john.doe@example.com'})

    # Get document reference example
    doc_ref = get_document_list('users')

    print(doc_ref)

    print(user_data)