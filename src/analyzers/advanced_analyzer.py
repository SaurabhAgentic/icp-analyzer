import spacy
from textblob import TextBlob
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import networkx as nx
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any, Tuple

class AdvancedAnalyzer:
    def __init__(self):
        """Initialize the advanced analyzer with required models and configurations."""
        # Load spaCy model for NLP tasks
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize TF-IDF vectorizer for topic modeling
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize LDA for topic modeling
        self.lda = LatentDirichletAllocation(
            n_components=5,
            random_state=42
        )
        
        # Initialize KMeans for customer segmentation
        self.kmeans = KMeans(
            n_clusters=4,
            random_state=42
        )
        
        # Define emotion keywords
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'delighted', 'thrilled', 'wonderful'],
            'sadness': ['disappointed', 'unhappy', 'frustrated', 'upset', 'poor'],
            'anger': ['angry', 'furious', 'annoyed', 'terrible', 'awful'],
            'fear': ['worried', 'concerned', 'anxious', 'nervous', 'scared'],
            'surprise': ['amazed', 'surprised', 'shocked', 'incredible', 'unexpected'],
            'trust': ['trust', 'reliable', 'confident', 'secure', 'dependable']
        }
    
    def analyze_testimonials(self, testimonials: List[str]) -> Dict[str, Any]:
        """Perform advanced analysis on testimonials."""
        # Convert testimonials to spaCy docs
        docs = [self.nlp(testimonial) for testimonial in testimonials]
        
        # Perform various analyses
        results = {
            'topic_modeling': self._perform_topic_modeling(testimonials),
            'named_entities': self._extract_named_entities(docs),
            'aspect_sentiment': self._analyze_aspect_sentiment(docs),
            'emotion_analysis': self._analyze_emotions(testimonials),
            'customer_segments': self._segment_customers(testimonials),
            'network_analysis': self._create_theme_network(docs),
            'time_series': self._analyze_time_series(testimonials),
            'anomaly_detection': self._detect_anomalies(testimonials)
        }
        
        return results
    
    def _perform_topic_modeling(self, testimonials: List[str]) -> Dict[str, Any]:
        """Perform topic modeling using LDA."""
        # Create document-term matrix
        dtm = self.vectorizer.fit_transform(testimonials)
        
        # Fit LDA
        self.lda.fit(dtm)
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Extract topics
        topics = []
        for topic_idx, topic in enumerate(self.lda.components_):
            top_terms = [feature_names[i] for i in topic.argsort()[:-10:-1]]
            topics.append({
                'topic_id': topic_idx,
                'top_terms': top_terms,
                'coherence_score': self._calculate_topic_coherence(topic, feature_names)
            })
        
        return {
            'topics': topics,
            'document_topics': self.lda.transform(dtm).tolist()
        }
    
    def _extract_named_entities(self, docs: List[spacy.tokens.Doc]) -> Dict[str, List[str]]:
        """Extract named entities from testimonials."""
        entities = {
            'organizations': [],
            'products': [],
            'features': [],
            'locations': []
        }
        
        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    entities['organizations'].append(ent.text)
                elif ent.label_ == 'PRODUCT':
                    entities['products'].append(ent.text)
                elif ent.label_ == 'FEATURE':
                    entities['features'].append(ent.text)
                elif ent.label_ == 'GPE':
                    entities['locations'].append(ent.text)
        
        return entities
    
    def _analyze_aspect_sentiment(self, docs: List[spacy.tokens.Doc]) -> Dict[str, Dict[str, float]]:
        """Perform aspect-based sentiment analysis."""
        aspects = {
            'product': [],
            'service': [],
            'support': [],
            'price': [],
            'features': []
        }
        
        aspect_keywords = {
            'product': ['product', 'solution', 'software', 'tool'],
            'service': ['service', 'delivery', 'implementation'],
            'support': ['support', 'help', 'assistance', 'response'],
            'price': ['price', 'cost', 'value', 'expensive', 'cheap'],
            'features': ['feature', 'functionality', 'capability']
        }
        
        for doc in docs:
            for aspect, keywords in aspect_keywords.items():
                for keyword in keywords:
                    if keyword in doc.text.lower():
                        # Extract the relevant sentence
                        for sent in doc.sents:
                            if keyword in sent.text.lower():
                                sentiment = TextBlob(sent.text).sentiment.polarity
                                aspects[aspect].append({
                                    'text': sent.text,
                                    'sentiment': sentiment
                                })
        
        # Calculate average sentiment for each aspect
        aspect_sentiments = {}
        for aspect, sentiments in aspects.items():
            if sentiments:
                avg_sentiment = sum(s['sentiment'] for s in sentiments) / len(sentiments)
                aspect_sentiments[aspect] = {
                    'average_sentiment': avg_sentiment,
                    'count': len(sentiments)
                }
        
        return aspect_sentiments
    
    def _analyze_emotions(self, testimonials: List[str]) -> Dict[str, float]:
        """Analyze emotions in testimonials."""
        emotion_counts = {emotion: 0 for emotion in self.emotion_keywords}
        total_mentions = 0
        
        for testimonial in testimonials:
            testimonial = testimonial.lower()
            for emotion, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    if keyword in testimonial:
                        emotion_counts[emotion] += 1
                        total_mentions += 1
        
        # Calculate emotion percentages
        emotion_percentages = {}
        for emotion, count in emotion_counts.items():
            if total_mentions > 0:
                emotion_percentages[emotion] = count / total_mentions
            else:
                emotion_percentages[emotion] = 0
        
        return emotion_percentages
    
    def _segment_customers(self, testimonials: List[str]) -> Dict[str, Any]:
        """Perform customer segmentation using clustering."""
        # Create TF-IDF features
        features = self.vectorizer.fit_transform(testimonials)
        
        # Perform clustering
        clusters = self.kmeans.fit_predict(features)
        
        # Analyze each cluster
        segment_analysis = {}
        for i in range(self.kmeans.n_clusters):
            cluster_docs = [doc for j, doc in enumerate(testimonials) if clusters[j] == i]
            
            # Get top terms for this cluster
            cluster_vectorizer = TfidfVectorizer(max_features=10)
            cluster_features = cluster_vectorizer.fit_transform(cluster_docs)
            top_terms = cluster_vectorizer.get_feature_names_out()
            
            # Calculate sentiment for this cluster
            cluster_sentiment = np.mean([
                TextBlob(doc).sentiment.polarity for doc in cluster_docs
            ])
            
            segment_analysis[f'segment_{i}'] = {
                'size': len(cluster_docs),
                'top_terms': top_terms.tolist(),
                'average_sentiment': float(cluster_sentiment),
                'percentage': len(cluster_docs) / len(testimonials)
            }
        
        return segment_analysis
    
    def _create_theme_network(self, docs: List[spacy.tokens.Doc]) -> Dict[str, Any]:
        """Create a network graph of themes and their relationships."""
        # Extract key terms and their relationships
        G = nx.Graph()
        
        for doc in docs:
            # Extract noun phrases and their relationships
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Only consider multi-word phrases
                    G.add_node(chunk.text)
                    
                    # Find related terms in the same sentence
                    for other_chunk in doc.noun_chunks:
                        if chunk != other_chunk and len(other_chunk.text.split()) >= 2:
                            if chunk.sent == other_chunk.sent:
                                G.add_edge(chunk.text, other_chunk.text)
        
        # Calculate network metrics
        metrics = {
            'nodes': list(G.nodes()),
            'edges': list(G.edges()),
            'centrality': nx.degree_centrality(G),
            'clustering': nx.clustering(G)
        }
        
        return metrics
    
    def _analyze_time_series(self, testimonials: List[str]) -> Dict[str, Any]:
        """Analyze trends over time."""
        # Create a time series of sentiment scores
        dates = [datetime.now() - timedelta(days=i) for i in range(len(testimonials))]
        sentiments = [TextBlob(testimonial).sentiment.polarity for testimonial in testimonials]
        
        # Create DataFrame for analysis
        df = pd.DataFrame({
            'date': dates,
            'sentiment': sentiments
        })
        
        # Calculate moving averages
        df['ma7'] = df['sentiment'].rolling(window=7).mean()
        df['ma30'] = df['sentiment'].rolling(window=30).mean()
        
        # Calculate trend
        z = np.polyfit(range(len(df)), df['sentiment'], 1)
        trend = np.poly1d(z)
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'sentiments': sentiments,
            'moving_averages': {
                '7_day': df['ma7'].tolist(),
                '30_day': df['ma30'].tolist()
            },
            'trend': {
                'slope': float(z[0]),
                'intercept': float(z[1])
            }
        }
    
    def _detect_anomalies(self, testimonials: List[str]) -> List[Dict[str, Any]]:
        """Detect anomalous testimonials using statistical methods."""
        # Calculate sentiment scores
        sentiments = [TextBlob(testimonial).sentiment.polarity for testimonial in testimonials]
        
        # Calculate statistics
        mean_sentiment = np.mean(sentiments)
        std_sentiment = np.std(sentiments)
        
        # Define anomaly thresholds
        upper_threshold = mean_sentiment + 2 * std_sentiment
        lower_threshold = mean_sentiment - 2 * std_sentiment
        
        # Find anomalies
        anomalies = []
        for i, (testimonial, sentiment) in enumerate(zip(testimonials, sentiments)):
            if sentiment > upper_threshold or sentiment < lower_threshold:
                anomalies.append({
                    'index': i,
                    'text': testimonial,
                    'sentiment': sentiment,
                    'type': 'high' if sentiment > upper_threshold else 'low'
                })
        
        return anomalies
    
    def _calculate_topic_coherence(self, topic: np.ndarray, feature_names: np.ndarray) -> float:
        """Calculate topic coherence score."""
        # Get top terms
        top_terms = [feature_names[i] for i in topic.argsort()[:-10:-1]]
        
        # Calculate pairwise similarity between terms
        similarities = []
        for i in range(len(top_terms)):
            for j in range(i + 1, len(top_terms)):
                term1 = self.nlp(top_terms[i])
                term2 = self.nlp(top_terms[j])
                similarity = term1.similarity(term2)
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def generate_visualizations(self, analysis_results: Dict[str, Any], output_dir: str) -> List[str]:
        """Generate and save visualizations for the analysis results."""
        os.makedirs(output_dir, exist_ok=True)
        visualization_files = []
        
        # 1. Topic Distribution
        plt.figure(figsize=(10, 6))
        topic_dist = np.array([topic['coherence_score'] for topic in analysis_results['topic_modeling']['topics']])
        plt.bar(range(len(topic_dist)), topic_dist)
        plt.title('Topic Distribution')
        plt.xlabel('Topic ID')
        plt.ylabel('Coherence Score')
        plt.savefig(os.path.join(output_dir, 'topic_distribution.png'))
        visualization_files.append('topic_distribution.png')
        
        # 2. Emotion Analysis
        plt.figure(figsize=(10, 6))
        emotions = list(analysis_results['emotion_analysis'].keys())
        values = list(analysis_results['emotion_analysis'].values())
        plt.bar(emotions, values)
        plt.title('Emotion Distribution')
        plt.xticks(rotation=45)
        plt.ylabel('Percentage')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'emotion_distribution.png'))
        visualization_files.append('emotion_distribution.png')
        
        # 3. Aspect Sentiment
        plt.figure(figsize=(10, 6))
        aspects = list(analysis_results['aspect_sentiment'].keys())
        sentiments = [data['average_sentiment'] for data in analysis_results['aspect_sentiment'].values()]
        plt.bar(aspects, sentiments)
        plt.title('Aspect-Based Sentiment Analysis')
        plt.xticks(rotation=45)
        plt.ylabel('Average Sentiment')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'aspect_sentiment.png'))
        visualization_files.append('aspect_sentiment.png')
        
        # 4. Time Series
        plt.figure(figsize=(12, 6))
        dates = analysis_results['time_series']['dates']
        sentiments = analysis_results['time_series']['sentiments']
        ma7 = analysis_results['time_series']['moving_averages']['7_day']
        ma30 = analysis_results['time_series']['moving_averages']['30_day']
        
        plt.plot(dates, sentiments, label='Daily Sentiment', alpha=0.5)
        plt.plot(dates, ma7, label='7-Day Moving Average')
        plt.plot(dates, ma30, label='30-Day Moving Average')
        plt.title('Sentiment Time Series')
        plt.xlabel('Date')
        plt.ylabel('Sentiment')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'sentiment_time_series.png'))
        visualization_files.append('sentiment_time_series.png')
        
        return visualization_files 