import re
import textstat
import language_tool_python
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt

def check_spelling_grammar(email_text):
    try:
        tool = language_tool_python.LanguageToolPublicAPI('en-US')
    except:
        print("Error: LanguageTool server not available.")
        return 6, ["LanguageTool server issue."]
    
    matches = tool.check(email_text)
    num_errors = len(matches)
    
    if num_errors == 0:
        score = 10
    elif num_errors < 5:
        score = 9
    elif num_errors < 10:
        score = 8
    else:
        score = 6
    
    return score, [match.message for match in matches]

def check_tone(email_text):
    blob = TextBlob(email_text)
    sentiment = blob.sentiment.polarity  
    
    if sentiment > 0.2:
        score = 9
    elif sentiment > 0:
        score = 8
    elif sentiment == 0:
        score = 7
    else:
        score = 6
    
    return score, sentiment

def check_clarity(email_text):
    readability_score = textstat.flesch_reading_ease(email_text)
    
    if readability_score > 60:
        score = 9
    elif readability_score > 50:
        score = 8
    else:
        score = 7
    
    return score, readability_score

def check_structure(email_text):
    structure_score = 10
    
    greeting = re.search(r'\b(hello|hi|dear|hey|greetings)\b', email_text, re.IGNORECASE)
    if not greeting:
        structure_score -= 2
    
    sign_off = re.search(r'\b(regards|best|thank you|sincerely)\b', email_text, re.IGNORECASE)
    if not sign_off:
        structure_score -= 2
    
    header = re.search(r'update on your claim|important information', email_text, re.IGNORECASE)
    if not header:
        structure_score -= 2
    
    footer = re.search(r'contact|support@|www\.', email_text, re.IGNORECASE)
    if not footer:
        structure_score -= 2
    
    return structure_score

def evaluate_email(agent_name, email_text):
    if not email_text.strip():
        print("Error: No email content provided.")
        return {}

    spelling_grammar_score, grammar_issues = check_spelling_grammar(email_text)
    tone_score, sentiment = check_tone(email_text)
    clarity_score, readability = check_clarity(email_text)
    structure_score = check_structure(email_text)
    
    overall_score = (spelling_grammar_score + tone_score + clarity_score + structure_score) / 4
    
    feedback = {
        "Agent Name": agent_name,
        "Spelling & Grammar Score": spelling_grammar_score,
        "Tone & Empathy Score": tone_score,
        "Clarity Score": clarity_score,
        "Structure Score": structure_score,
        "Overall Score": round(overall_score, 2),
        "Grammar Issues": ', '.join(grammar_issues) if grammar_issues else 'None',
        "Sentiment Score": round(sentiment, 2),
        "Readability Score": round(readability, 2)
    }
    
    return feedback

def export_reports(reports, filename="email_qc_report.csv"):
    df = pd.DataFrame(reports)
    df.to_csv(filename, index=False)
    print(f"Report exported successfully as {filename}")

def visualize_report(report):
    labels = ["Spelling & Grammar", "Tone & Empathy", "Clarity", "Structure", "Overall"]
    scores = [
        report["Spelling & Grammar Score"],
        report["Tone & Empathy Score"],
        report["Clarity Score"],
        report["Structure Score"],
        report["Overall Score"]
    ]
    
    colors = plt.cm.Paired.colors  
    plt.figure(figsize=(8,5))
    plt.bar(labels, scores, color=colors[:len(labels)])
    plt.ylim(0, 10)
    plt.ylabel("Score")
    plt.title(f"Email Quality Report for {report['Agent Name']}")
    plt.show()

if __name__ == "__main__":
    agent_name = input("Enter Agent Name: ")
    email_text = input("Enter email text:\n")
    
    report = evaluate_email(agent_name, email_text)
    if report:
        export_reports([report])
        visualize_report(report)

        for key, value in report.items():
            print(f"{key}: {value}")
