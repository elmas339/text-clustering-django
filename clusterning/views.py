from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TextClusteringResult, ClusteredText
import pandas as pd
from joblib import load
import os
from django.conf import settings
import json
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def preprocess_text(text):
    # Convert to string first to avoid the error
    text = str(text)
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)  # Remove special characters
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words and len(word) > 3]
    return ' '.join(tokens) if tokens else ''


def load_models():
    base_dir = os.path.join(settings.BASE_DIR, 'clusterning', 'ia')
    return {
        'kmeans': load(os.path.join(base_dir, 'kmeans_model.joblib')),
        'vectorizer': load(os.path.join(base_dir, 'tfidf_vectorizer.joblib')),
        'svd': load(os.path.join(base_dir, 'svd.joblib')),
        'scaler': load(os.path.join(base_dir, 'scaler.joblib'))
    }


def upload_file(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        try:
            file = request.FILES['file']
            df = pd.read_csv(file)

            # Load models
            models = load_models()

            # Preprocess and predict
            text_column = df.columns[0]
            texts = df[text_column].tolist()

            # Apply preprocessing to match training pipeline
            preprocessed_texts = [preprocess_text(text) for text in texts]

            # Prediction pipeline using preprocessed texts
            vectors = models['vectorizer'].transform(preprocessed_texts)
            reduced_vectors = models['svd'].transform(vectors)
            normalized_vectors = models['scaler'].transform(reduced_vectors)
            clusters = models['kmeans'].predict(normalized_vectors)

            # Save results
            result = TextClusteringResult.objects.create(
                file_name=file.name,
                num_clusters=len(set(clusters))
            )

            # Save clustered texts
            for text, cluster in zip(texts, clusters):
                ClusteredText.objects.create(
                    result=result,
                    original_text=text,
                    cluster_number=int(cluster)
                )

            return JsonResponse({
                'success': True,
                'result_id': result.id
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'clustering/upload.html')


def view_results(request, result_id):
    try:
        result = TextClusteringResult.objects.get(id=result_id)
        clustered_texts = ClusteredText.objects.filter(result=result)

        # Organize data for visualization
        clusters_data = {}
        for text in clustered_texts:
            if text.cluster_number not in clusters_data:
                clusters_data[text.cluster_number] = []
            clusters_data[text.cluster_number].append(text.original_text)

        context = {
            'result': result,
            'clusters_data': clusters_data
        }

        return render(request, 'clustering/results.html', context)

    except TextClusteringResult.DoesNotExist:
        return JsonResponse({'error': 'Result not found'}, status=404)