from transformers import pipeline
summarizer=pipeline('summarization',model='facebook/bart-large-cnn')

def summarize_text(text):
 return summarizer(text[:3000])[0]['summary_text']