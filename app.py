from flask import Flask, render_template, request, redirect, url_for, session
import jsonify
from paragraph_flow_analyzer import ParagraphFlowAnalyzer
from proposition_extractor import PropositionExtractor
from purge_graphs import cleanup_files

import os

app = Flask(__name__)
app.secret_key = 'walorguiawefasdfjklh'
directory_path = "/Users/claireli/_abc/_pr/lexical-to-symbolic-logic-engine/_example_articles/_google_news"
proposition_extractor = PropositionExtractor()

csv_path = 'similarity_scores.csv'

@app.route('/extract-propositions', methods=['POST'])
def handle_extract_propositions():
    data = request.json
    conn_i = int(data.get('conn_i'))
    conn_j = int(data.get('conn_j'))
    print("DEBUG")
    print(''.join(['='*80]))

    paragraphs = session.get('paragraphs', {})
    paragraph_i = paragraphs[conn_i] if conn_i < len(paragraphs) else ""
    paragraph_j = paragraphs[conn_j] if conn_j < len(paragraphs) else ""

    propositions_i = proposition_extractor.extract_propositions(paragraph_i)
    propositions_j = proposition_extractor.extract_propositions(paragraph_j)
    total_propositions = propositions_i + propositions_j
    print("Propositions found;", total_propositions)
    implications = proposition_extractor.find_implications(total_propositions)
    print("Implications found:", implications)

    result = {
        'propositions_i': propositions_i,
        'propositions_j': propositions_j,
        'edges': implications,
    }
    return result 

@app.route('/', methods=['GET'])
def index():
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    cleanup_files()
    
    selected_file = request.args.get('selected_file', None)
    image_path = None
    content = None
    key_phrases_data = None
    connections = None

    if selected_file:
        full_path = os.path.join(directory_path, selected_file)
        with open(full_path, 'r') as file:
            content = file.read().split('<p>')
        analyzer = ParagraphFlowAnalyzer(directory_path)
        paragraphs = analyzer.articles_paragraphs[selected_file]
        session['paragraphs'] = paragraphs
        phrases = analyzer.articles_phrases[selected_file]
        G = analyzer.build_thematic_graph(phrases)
        image_path = analyzer.visualize_graph(G)
        image_path = '/'.join(image_path.split('/')[1:])
        print(image_path)
        connections = analyzer.parse_similarity_csv(csv_path)
        key_phrases_data = {'phrases': phrases, 'paragraphs': paragraphs}
    return render_template('index.html', files=files, image_path=image_path, content=content, key_phrases_data=key_phrases_data, connections=connections)


@app.route('/select_file', methods=['POST'])
def select_file():
    selected_file = request.form['file_selector']
    print("Selected file:", selected_file)  # Example processing
    return redirect(url_for('index', selected_file=selected_file))

#@app.route('/select_file')
#@app.route('/')
#def index():
    #directory_path = "/Users/claireli/_abc/_pr/_example_articles/_google_news"
    #files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    #analyzer = ParagraphFlowAnalyzer(articles_paragraphs)
    #image_path = "path/to/generated/graph/image.png"  # Adjust based on your graph generation logic

    #return render_template('index.html', image_path=image_path, files=files)


if __name__ == '__main__':
    app.run(debug=True, port=7007)
