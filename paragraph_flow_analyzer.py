import nltk
from datetime import datetime
import os
import csv
import spacy
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Set Matplotlib to use the Agg backend
import matplotlib.pyplot as plt
import string
nltk.download('stopwords')
nltk.download('punkt')
from article_reader import ArticleReader

class ParagraphFlowAnalyzer:
  def __init__(self, article_path):
    self.nlp = spacy.load("en_core_web_sm")
    self.directory_path = article_path
    self.articles = ArticleReader.read_articles_from_directory(self.directory_path)
    self.articles_paragraphs = self.split_articles_into_paragraphs()
    self.articles_phrases = self.extract_significant_phrases_for_all()
    self.preprocessed_articles_paragraphs = self.preprocess_articles_paragraphs()
    self.graph = None

  def split_articles_into_paragraphs(self):
    """
    Split the contents of each article into paragraphs and store them in a dictionary.
    """
    articles_paragraphs = {}
    for filename, article_text in self.articles.items():
        paragraphs = article_text.split('\n\n')  # Splitting by two newlines as a paragraph delimiter
        articles_paragraphs[filename] = paragraphs
    return articles_paragraphs

  def preprocess_articles_paragraphs(self):
    """
    Preprocess each paragraph of each article to extract keywords.
    Stores the preprocessed paragraphs in a dictionary mirroring the structure of self.articles_paragraphs.
    """
    preprocessed_articles_paragraphs = {}
    for filename, paragraphs in self.articles_paragraphs.items():
        preprocessed_paragraphs = [self.preprocess_text(paragraph) for paragraph in paragraphs]
        preprocessed_articles_paragraphs[filename] = preprocessed_paragraphs
    return preprocessed_articles_paragraphs

  def preprocess_text(self, text):
    """
    Tokenize, remove punctuation, lowercase, remove stopwords, and stem the text.
    """
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [ps.stem(word) for word in tokens]
    return tokens

  def build_graph(self):
    """
    Build a directed graph from the paragraphs based on shared keywords.
    """
    G = nx.DiGraph()
    paragraph_keywords = [self.preprocess_text(paragraph) for paragraph in self.articles_paragraphs]

    for i, _ in enumerate(paragraph_keywords):
        G.add_node(i, keywords=paragraph_keywords[i])

    for i, keywords_i in enumerate(paragraph_keywords):
        for j, keywords_j in enumerate(paragraph_keywords):
            if i != j and set(keywords_i) & set(keywords_j):
                G.add_edge(i, j)
                
    self.graph = G

  def analyze_flow(self):
    """
    Analyze the paragraph flow using graph theory metrics.
    """
    if self.graph is None:
        self.build_graph()

    # Analysis examples
    strongly_connected_components = list(nx.strongly_connected_components(self.graph))
    pagerank = nx.pagerank(self.graph)

    return strongly_connected_components, pagerank

  def build_thematic_graph(self, article_phrases, threshold=0.1, csv_filename="similarity_scores.csv"):
    """
    Build a thematic graph for an article based on phrase similarity.
    """
    G = nx.Graph()
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(['Similarity Score', 'Paragraph i', 'i Phrases', 'Paragraph j', 'j Phrases'])  # Header

      for i in range(len(article_phrases)):
        for j in range(i + 1, len(article_phrases)):
          similarity = self.calculate_jaccard_similarity(set(article_phrases[i]), set(article_phrases[j]))
          if similarity > threshold:
            G.add_edge(i, j, weight=similarity)
            # Convert phrase lists to strings for CSV output
            i_phrases_str = ', '.join(article_phrases[i])
            j_phrases_str = ', '.join(article_phrases[j])
            writer.writerow([similarity, i, i_phrases_str, j, j_phrases_str])

      return G

  def visualize_graph(self, G):
    """
    Visualize a graph with paragraph nodes
    """
    # TODO: move into cfg
    pos = nx.spring_layout(G, k=0.5)  
    plt.figure(figsize=(10, 8))  
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_weight='bold')
    save_dir = "static/graph_images"
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(save_dir, f"graph_{timestamp}.png")

    plt.savefig(image_path)
    plt.close()  
    print(f"Graph image saved to: {image_path}")
    return image_path  


  def extract_significant_phrases(self, text):
    """
    Extract significant phrases from a text using spaCy for NLP tasks.
    """
    doc = self.nlp(text)
    return [chunk.text for chunk in doc.noun_chunks]

  def extract_significant_phrases_for_all(self):
    """
    Apply phrase extraction to all paragraphs of all articles.
    """
    return {filename: [self.extract_significant_phrases(paragraph) for paragraph in paragraphs]
      for filename, paragraphs in self.articles_paragraphs.items()}

  def calculate_jaccard_similarity(self, set1, set2):
    """
    Calculate the Jaccard similarity between two sets of phrases.
    """
    intersection = len(set(set1) & set(set2))
    union = len(set(set1) | set(set2))
    return intersection / union if union != 0 else 0

  def parse_similarity_csv(self, csv_path):
    connections = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
          connection = {
            'i': row['Paragraph i'],
            'j': row['Paragraph j'],
            'i_phrases': row['i Phrases'],
            'j_phrases': row['j Phrases']
          }
          connections.append(connection)
    return connections


if __name__ == "__main__":
    directory_path = "/Users/claireli/_abc/_pr/_example_articles/_google_news"
    filename = "seed_stage_cto_interview.2.txt"
    analyzer = ParagraphFlowAnalyzer(directory_path)

    paragraphs = analyzer.articles_paragraphs[filename]
    article_phrases = analyzer.articles_phrases[filename]
    for p in range(len(article_phrases)):
        print(f"{p} -> {article_phrases[p]}")
    G = analyzer.build_thematic_graph(article_phrases)
    analyzer.visualize_graph(G)
