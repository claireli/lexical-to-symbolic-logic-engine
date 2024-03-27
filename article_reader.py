# Usage: import article_reader
# Read all txt article files in the directory_path

import os

class ArticleReader:
  @staticmethod
  def read_articles_from_directory(directory_path):
    articles = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
                articles[filename] = file.read()
    return articles
