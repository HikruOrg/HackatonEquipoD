from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import json
import os
from pathlib import Path
from typing import List, Tuple, Dict
import time

class AzureImageClassifier:
    """Azure Computer Vision-based image classifier."""
    
    def __init__(self, endpoint: str = None, key: str = None):
        """
        Initialize Azure Computer Vision client.
        
        Args:
            endpoint: Azure Computer Vision endpoint URL
            key: Azure Computer Vision subscription key
        """
        self.endpoint = endpoint or os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
        self.key = key or os.getenv("AZURE_COMPUTER_VISION_KEY")
        
        if not self.endpoint or not self.key:
            raise ValueError(
                "Azure Computer Vision endpoint and key are required. "
                "Provide them as parameters or set AZURE_COMPUTER_VISION_ENDPOINT "
                "and AZURE_COMPUTER_VISION_KEY environment variables."
            )
        
        # Initialize the Computer Vision client
        self.client = ComputerVisionClient(
            self.endpoint, 
            CognitiveServicesCredentials(self.key)
        )
    
    def classify_image(self, img_path: str, candidate_labels: List[str] = None) -> List[Tuple[str, float]]:
        """
        Classify image using Azure Computer Vision.
        
        Args:
            img_path: Path to image file
            candidate_labels: List of candidate labels (used for filtering/mapping)
            
        Returns:
            List of (label, confidence_score) tuples
        """
        try:
            # Read image file
            with open(img_path, "rb") as image_stream:
                # Get image analysis with tags and categories
                analysis = self.client.analyze_image_in_stream(
                    image_stream,
                    visual_features=['Tags', 'Categories', 'Objects', 'Description']
                )
            
            results = []
            
            # Extract tags with confidence scores
            if analysis.tags:
                for tag in analysis.tags:
                    results.append((tag.name.lower(), tag.confidence))
            
            # Extract categories with confidence scores
            if analysis.categories:
                for category in analysis.categories:
                    # Extract category name (remove score prefix like "abstract_")
                    category_name = category.name.split('_')[-1] if '_' in category.name else category.name
                    results.append((category_name.lower(), category.score))
            
            # Extract objects with confidence scores
            if analysis.objects:
                for obj in analysis.objects:
                    results.append((obj.object_property.lower(), obj.confidence))
            
            # Extract description captions
            if analysis.description and analysis.description.captions:
                for caption in analysis.description.captions:
                    # Split caption into words and add with caption confidence
                    words = caption.text.lower().split()
                    for word in words:
                        if len(word) > 2:  # Filter out short words
                            results.append((word, caption.confidence))
            
            # Remove duplicates and sort by confidence
            unique_results = {}
            for label, score in results:
                if label in unique_results:
                    # Keep the highest confidence score
                    unique_results[label] = max(unique_results[label], score)
                else:
                    unique_results[label] = score
            
            # Convert back to list and sort by confidence
            final_results = [(label, score) for label, score in unique_results.items()]
            final_results.sort(key=lambda x: x[1], reverse=True)
            
            return final_results
            
        except Exception as e:
            print(f"Error classifying image {img_path}: {str(e)}")
            return []

# Global classifier instance
_azure_classifier = None

def get_classifier(endpoint: str = None, key: str = None) -> AzureImageClassifier:
    """Get or create Azure classifier instance."""
    global _azure_classifier
    if _azure_classifier is None:
        _azure_classifier = AzureImageClassifier(endpoint, key)
    return _azure_classifier

def load_categories(json_path: str):
    with open(json_path, "r") as f:
        return json.load(f)

def flatten_labels(categories_dict):
    """Devuelve lista de labels base a usar como candidatos."""
    labels = []
    for lst in categories_dict.values():
        labels.extend(lst)
    return list(set(labels))

def classify_image(img_path, candidate_labels, azure_endpoint: str = None, azure_key: str = None):
    """
    Clasifica una sola imagen usando Azure Computer Vision.
    
    Args:
        img_path: Path to image file
        candidate_labels: List of candidate labels (for compatibility)
        azure_endpoint: Azure Computer Vision endpoint
        azure_key: Azure Computer Vision key
    """
    try:
        classifier = get_classifier(azure_endpoint, azure_key)
        return classifier.classify_image(str(img_path), candidate_labels)
    except Exception as e:
        print(f"Error in classify_image: {str(e)}")
        return []

def map_to_groups(results, mapping):
    """
    Agrupa etiquetas según categories.json y promedia confianza.
    Enhanced to handle partial matches and synonyms.
    """
    grouped = {}
    
    for label, score in results:
        label_lower = label.lower().strip()
        
        # Direct match first
        for group, labels in mapping.items():
            labels_lower = [l.lower().strip() for l in labels]
            if label_lower in labels_lower:
                grouped[group] = grouped.get(group, []) + [score]
                break
        else:
            # Partial match - check if label contains any of the category words
            for group, labels in mapping.items():
                for category_label in labels:
                    category_lower = category_label.lower().strip()
                    # Check for substring matches (both ways)
                    if (category_lower in label_lower or label_lower in category_lower) and len(category_lower) > 2:
                        grouped[group] = grouped.get(group, []) + [score * 0.8]  # Reduce confidence for partial matches
                        break
                if group in grouped:
                    break
    
    # Calculate weighted average per group
    final_groups = {}
    for group, scores in grouped.items():
        if scores:
            # Use weighted average, giving more weight to higher confidence scores
            sorted_scores = sorted(scores, reverse=True)
            if len(sorted_scores) == 1:
                final_groups[group] = sorted_scores[0]
            else:
                # Weighted average: first score gets full weight, others get diminishing weight
                weights = [1.0] + [0.8 ** i for i in range(1, len(sorted_scores))]
                weighted_sum = sum(score * weight for score, weight in zip(sorted_scores, weights))
                weight_sum = sum(weights)
                final_groups[group] = weighted_sum / weight_sum
    
    return final_groups
