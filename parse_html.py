from bs4 import BeautifulSoup
import json

def parse_quiz_structure(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find all select elements (dropdowns)
    dropdowns = soup.find_all('select', class_='question_input')
    
    quiz_structure = []
    for dropdown in dropdowns:
        dropdown_id = dropdown.get('id')
        dropdown_name = dropdown.get('name')
        
        # Get the question text from the nearest parent div with class 'question_text'
        question_div = dropdown.find_parent('div', class_='question_text')
        question_text = question_div.get_text(strip=True) if question_div else "Question text not found"
        
        # Get available options
        options = []
        for option in dropdown.find_all('option'):
            if option.get('value') and option.get('value') != '':  # Skip the "Select" placeholder
                options.append({
                    'value': option.get('value'),
                    'text': option.text.strip('"')  # Clean up the text
                })
        
        quiz_structure.append({
            'id': dropdown_id,
            'name': dropdown_name,
            'question': question_text,
            'options': options
        })
    
    # Save to JSON file
    with open('quiz_structure.json', 'w') as f:
        json.dump(quiz_structure, f, indent=2)
    
    return quiz_structure

if __name__ == "__main__":
    structure = parse_quiz_structure('actual_quiz.html')
    print("Quiz structure has been saved to quiz_structure.json")
    print("\nPreview of the structure:")
    for item in structure:
        print(f"\nDropdown ID: {item['id']}")
        print(f"Question: {item['question'][:100]}...")
        print("Options:")
        for opt in item['options']:
            print(f"  - {opt['text']} (value={opt['value']})")
