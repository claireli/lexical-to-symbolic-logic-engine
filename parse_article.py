import os
import csv
import string
from collections import Counter

directory_path = '/Users/claireli/_abc/_pr/_example_articles/_google_news'
output_csv_path = '/Users/claireli/_abc/_pr/_example_articles/_google_news/article_analysis.csv'

def preprocess_text(text):
  stop_words = set(["the", "and", "to", "our", "a", "in", "of", "for", "on", "is", "with", "that", "by", "as", "are", "it", "this", "be", "from", "or", "which", "an", "we"])
  text = text.lower()  
  text = text.translate(str.maketrans('', '', string.punctuation))  
  words = [word for word in text.split() if word not in stop_words]

  return ' '.join(words)

def read_articles_from_directory(directory_path):
  articles = {}
  for filename in os.listdir(directory_path):
    if filename.endswith('.txt'):
      with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
        articles[filename] = file.read()
  return articles

def analyze_articles(articles):
  word_counts = {}
  word_frequencies = {}
  for filename, article in articles.items():
    preprocessed_article = preprocess_text(article)
    words = preprocessed_article.split()
    word_counts[filename] = len(words)
    word_frequencies[filename] = Counter(words).most_common(10)
  return word_counts, word_frequencies

def write_analysis_to_csv(output_csv_path, articles, word_counts, word_frequencies):
  with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Article Filename', 'Word Count', 'Common Words'])
    for filename in articles.keys():
      top_10_words_freqs = ', '.join([f"{word}: {freq}" for word, freq in word_frequencies[filename]])
      writer.writerow([filename, word_counts[filename], top_10_words_freqs])

if __name__ == '__init__':
  articles = read_articles_from_directory(directory_path)
  word_counts, word_frequencies = analyze_articles(articles)
  write_analysis_to_csv(output_csv_path, articles, word_counts, word_frequencies)
