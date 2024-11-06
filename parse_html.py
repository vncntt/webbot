import os
from bs4 import BeautifulSoup
import json

def parse_quiz_structure(html_file):
    # print(f"\nParse HTML Debug:")
    # print(f"Received file path: {html_file}")
    # print(f"File exists: {os.path.exists(html_file)}")
    
    quiz_dir = os.path.dirname(html_file)
    json_path = os.path.join(quiz_dir, 'quiz_structure.json')
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"Read {len(content)} bytes")
        
    soup = BeautifulSoup(content, 'html.parser')
    questions = soup.find_all('div', class_='display_question')
    print(f"Found {len(questions)} questions")
    
    quiz_structure = []
    
    # Find all question divs
    for question in questions:
        try:
            # More flexible question type finding
            question_type_elem = question.find('span', class_='question_type')
            if not question_type_elem:
                print(f"Warning: No question type found for question")
                continue
            question_type = question_type_elem.text.strip()
            
            # More flexible question text finding
            question_text_elem = question.find('div', class_='question_text')
            if not question_text_elem:
                print(f"Warning: No question text found for question")
                continue
            question_text = question_text_elem.get_text(strip=True)
            
            if question_type == 'multiple_choice_question':
                # Handle multiple choice questions
                name = question.find('input', class_='question_input')['name']
                options = []
                
                for answer in question.find_all('div', class_='answer'):
                    radio_input = answer.find('input', type='radio')
                    label = answer.find('div', class_='answer_label')
                    if radio_input and label:
                        options.append({
                            'value': radio_input['value'],
                            'text': label.get_text(strip=True).strip('"')
                        })
                
                quiz_structure.append({
                    'id': None,
                    'name': name,
                    'question': question_text,
                    'options': options,
                    'type': 'multiple_choice'
                })
                
            elif question_type in ['matching_question', 'multiple_dropdowns_question']:
                # Handle dropdown questions (existing logic)
                dropdowns = question.find_all('select', {'class': 'question_input'})
                for dropdown in dropdowns:
                    dropdown_id = dropdown.get('id')
                    dropdown_name = dropdown.get('name')
                    
                    options = []
                    for option in dropdown.find_all('option'):
                        if option.get('value') and option.get('value') != '':
                            options.append({
                                'value': option.get('value'),
                                'text': option.text.strip().strip('"')
                            })
                    
                    if dropdown_id or dropdown_name:
                        quiz_structure.append({
                            'id': dropdown_id,
                            'name': dropdown_name,
                            'question': question_text,
                            'options': options,
                            'type': 'dropdown'
                        })
                
        except Exception as e:
            print(f"Error parsing question: {str(e)}")
            continue
    
    # Save to JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(quiz_structure, f, indent=2, ensure_ascii=False)
    
    return quiz_structure

if __name__ == "__main__":
    # For testing directly, you can still use a hardcoded path
    import sys
    test_file = sys.argv[1] 
    structure = parse_quiz_structure(test_file)
    print(f"Quiz structure has been saved to {os.path.dirname(test_file)}/quiz_structure.json")
    print("\nPreview of the structure:")
    for item in structure:
        print(f"\nDropdown identifier: {item['id'] or item['name']}")
        print(f"Question: {item['question'][:100]}...")
        print("Options:")
        for opt in item['options']:
            print(f"  - {opt['text']} (value={opt['value']})")
