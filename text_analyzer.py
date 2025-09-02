import os
import re
from collections import defaultdict
import pandas as pd
from textblob import TextBlob
import nltk

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def load_word_list(file_path):
    """Load positive/negative words from file using absolute path"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, file_path)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Word list file not found: {full_path}")
    
    with open(full_path, 'r') as f:
        return set(word.strip().lower() for word in f.readlines() 
                 if not word.startswith(';') and word.strip())

class TextAnalyzer:
    def __init__(self):
        self.positive_words = load_word_list('positive-words.txt')
        self.negative_words = load_word_list('negative-words.txt')
        self.pronouns = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'}

    def analyze_text(self, text):
        """Calculate all 13 metrics for given text"""
        metrics = defaultdict(float)
        
        # Text processing
        blob = TextBlob(text)
        sentences = blob.sentences
        words = [word.lower() for word in blob.words if word.isalpha()]
        word_count = len(words)
        
        # Calculate metrics (1-13)
        pos_score = sum(1 for word in words if word in self.positive_words)
        neg_score = sum(1 for word in words if word in self.negative_words)
        polarity = (pos_score - neg_score) / ((pos_score + neg_score) + 0.000001)
        subjectivity = blob.sentiment.subjectivity
        avg_sent_len = word_count / len(sentences) if sentences else 0
        complex_words = [w for w in words if self.syllable_count(w) > 2]
        complex_pct = (len(complex_words) / word_count * 100) if word_count else 0
        fog_index = 0.4 * (avg_sent_len + complex_pct)
        
        return {
            'POSITIVE SCORE': pos_score,
            'NEGATIVE SCORE': neg_score,
            'POLARITY SCORE': polarity,
            'SUBJECTIVITY SCORE': subjectivity,
            'AVG SENTENCE LENGTH': avg_sent_len,
            'PERCENTAGE OF COMPLEX WORDS': complex_pct,
            'FOG INDEX': fog_index,
            'AVG NUMBER OF WORDS PER SENTENCE': avg_sent_len,
            'COMPLEX WORD COUNT': len(complex_words),
            'WORD COUNT': word_count,
            'SYLLABLE PER WORD': sum(self.syllable_count(w) for w in words) / word_count if word_count else 0,
            'PERSONAL PRONOUNS': sum(1 for w in words if w in self.pronouns),
            'AVG WORD LENGTH': sum(len(w) for w in words) / word_count if word_count else 0
        }

    def syllable_count(self, word):
        """Improved syllable counting algorithm"""
        word = word.lower()
        if len(word) <= 3:
            return 1
            
        count = 0
        vowels = "aeiouy"
        prev_char_was_vowel = False
        
        # Count vowel groups
        for char in word:
            if char in vowels and not prev_char_was_vowel:
                count += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
                
        # Adjust for special cases
        if word.endswith(('es', 'ed')) and not word.endswith(('les', 'led')):
            count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            count += 1
            
        return max(1, count)

def main():
    analyzer = TextAnalyzer()
    
    # Use absolute path for output directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'analyzed_results')
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = []
    
    # Process files using absolute paths
    input_dir = os.path.join(base_dir, 'extracted_articles')
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            metrics = analyzer.analyze_text(text)
            metrics['ARTICLE_ID'] = filename[:-4]  # Remove .txt extension
            all_results.append(metrics)
            print(f"Processed: {filename}")  # Debug output
    
    if all_results:
        df = pd.DataFrame(all_results)
        output_file = os.path.join(output_dir, 'all_metrics.csv')
        df.to_csv(output_file, index=False)
        print(f"\n✅ Analysis complete. Results saved to:\n{output_file}")
    else:
        print("\n⚠️ No articles processed. Please ensure:")
        print(f"- The 'extracted_articles' directory contains .txt files")
        print(f"- Directory structure: {os.path.abspath(base_dir)}")

if __name__ == '__main__':
    main()
