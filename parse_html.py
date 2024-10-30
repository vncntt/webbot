from bs4 import BeautifulSoup
import json

def parse_quiz_structure(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find all select elements (dropdowns) with either class 'question_input' or within question divs
    dropdowns = soup.find_all('select', {'class': 'question_input'})
    
    quiz_structure = []
    for dropdown in dropdowns:
        dropdown_id = dropdown.get('id')
        dropdown_name = dropdown.get('name')
        
        # Get the question text - try different parent structures
        question_text = "Question text not found"
        
        # First try finding the nearest parent div with class 'question_text'
        question_div = dropdown.find_parent('div', class_='question_text')
        if question_div:
            question_text = question_div.get_text(strip=True)
        else:
            # Try finding the nearest parent div with class 'display_question'
            display_div = dropdown.find_parent('div', class_='display_question')
            if display_div:
                # Look for the question text div within this container
                text_div = display_div.find('div', class_='question_text')
                if text_div:
                    question_text = text_div.get_text(strip=True)
        
        # Get available options
        options = []
        for option in dropdown.find_all('option'):
            if option.get('value') and option.get('value') != '':  # Skip empty/placeholder options
                options.append({
                    'value': option.get('value'),
                    'text': option.text.strip().strip('"')  # Clean up the text
                })
        
        # Only add if we found either an id or name
        if dropdown_id or dropdown_name:
            quiz_structure.append({
                'id': dropdown_id,
                'name': dropdown_name,
                'question': question_text,
                'options': options
            })
    
    # Save to JSON file
    with open('quiz_structure.json', 'w', encoding='utf-8') as f:
        json.dump(quiz_structure, f, indent=2, ensure_ascii=False)
    
    return quiz_structure

if __name__ == "__main__":
    structure = parse_quiz_structure('actual_quiz.html')
    print("Quiz structure has been saved to quiz_structure.json")
    print("\nPreview of the structure:")
    for item in structure:
        print(f"\nDropdown identifier: {item['id'] or item['name']}")
        print(f"Question: {item['question'][:100]}...")
        print("Options:")
        for opt in item['options']:
            print(f"  - {opt['text']} (value={opt['value']})")
