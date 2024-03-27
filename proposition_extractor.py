import nltk
from nltk.tokenize import sent_tokenize

class PropositionExtractor:
  def __init__(self):
    # Ensure nltk resources are downloaded (e.g., tokenizers)
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')

  def find_implications(self, propositions):
    """
    Evaluates each proposition against all others in the list to find implies relationships.
    
    :param propositions: A list of propositions to evaluate.
    :return: A dictionary where the key is a proposition (labeled with a capital letter),
             and the value is a list of propositions (labeled with capital letters) that it implies.
    """
    # Initialize the result dictionary
    edges = {}
    # Label each proposition with a capital letter
    labels = {index: chr(65 + index) for index, _ in enumerate(propositions)}
    print(labels, propositions)
    
    for i, P in enumerate(propositions):
        # Initialize the list of implies relationships for the current proposition
        edges[labels[i]] = []
        
        for j, Q in enumerate(propositions):
            if i != j:  # Ensure we're not comparing the proposition with itself
                if self.implies(P, Q):
                    # If P implies Q, add Q's label to P's list in the result dictionary
                    edges[labels[i]].append(labels[j])
    
    return edges

  def extract_propositions(self, p):
    """
    Extract propositions from a paragraph by identifying individual sentences.
    
    :param p: A string containing the paragraph content.
    :return: A list of sentences considered as propositions.
    """
    propositions = sent_tokenize(p)  # Tokenize paragraph into sentences
    return propositions

  
  def implies(self, P, Q):
    """
    :param P: The antecedent proposition.
    :param Q: The consequent proposition.
    :return: True if P implies Q, False otherwise.
    """
    return self.implies_relationship(P, Q)

  def implies_relationship(self,proposition1, proposition2):
    # Tokenization
    print("TOKENIZATION")
    tokens1 = nltk.word_tokenize(proposition1)
    tokens2 = nltk.word_tokenize(proposition2)
    #print(tokens1, tokens2)
  
    # Part-of-Speech (POS) Tagging
    print("PART OF SPEECH")
    pos_tags1 = nltk.pos_tag(tokens1)
    pos_tags2 = nltk.pos_tag(tokens2)
    #print(pos_tags1, pos_tags2)
    implication_patterns = [
        ("VB", "NN"),   # Verb followed by a noun
        ("VBZ", "NN"),  # Singular verb followed by a noun
        ("VBP", "NN"),  # Plural verb followed by a noun
        ("VB", "NNS"),  # Verb followed by a plural noun
        ("VBZ", "NNS"), # Singular verb followed by a plural noun
        ("VBP", "NNS"), # Plural verb followed by a plural noun
        ("NN", "NN"),   # Noun followed by another noun
        ("NN", "VB"),   # Noun followed by a verb
        ("NN", "VBZ"),  # Noun followed by a singular verb
        # Add more patterns as needed
    ]

    for word1, pos1 in pos_tags1:
        for word2, pos2 in pos_tags2:
            if (pos1, pos2) in implication_patterns and word1 == word2:
                return True
  
    return False
