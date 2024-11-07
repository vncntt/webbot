import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_answers(quiz_dir):
    """Load answers from answers.txt in the quiz directory"""
    answers = {}
    answers_path = os.path.join(quiz_dir, 'answers.txt')
    
    with open(answers_path, 'r') as f:
        for line in f:
            if line.strip():
                # Remove "Question " prefix and split on first colon
                line = line.replace("Question ", "")
                question_id, answer = line.strip().split(": ", 1)
                answers[question_id] = answer
    return answers

def submit_final_answers(driver, quiz_dir, quiz_url):
    try:
        # Load answers
        answers = parse_answers(quiz_dir)
        
        print(f"Navigating to quiz page: {quiz_url}")
        driver.get(quiz_url)
        
        # Click "Take Quiz Again" button or similar
        retake_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Take the Quiz Again')] | //a[contains(text(), 'Take the Quiz Again')] | //button[contains(text(), 'Resume Quiz')] | //a[contains(text(), 'Resume Quiz')] | //button[contains(text(), 'Take the Quiz')] | //a[contains(text(), 'Take the Quiz')]"))
        )
        retake_button.click()
        
        # Wait for quiz form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submit_quiz_form"))
        )
        
        # Fill in all answers at once
        for question_id, answer in answers.items():
            try:
                print(f"\nSubmitting answer for {question_id}")
                
                # Find all radio buttons for this question
                radio_buttons = driver.find_elements(By.CSS_SELECTOR, f"input[type='radio'][name='{question_id}']")
                
                if radio_buttons:
                    print(f"Found {len(radio_buttons)} radio buttons")
                    # Find all answer labels
                    labels = driver.find_elements(By.CSS_SELECTOR, f"div[class='answer_label']")
                    
                    # Match answer with label and click corresponding radio button
                    for i, label in enumerate(labels):
                        text = label.text.strip().strip('"')
                        if text == answer.strip().strip('"'):
                            radio_buttons[i].click()
                            print(f"Selected: {text}")
                            break
                else:
                    # If no radio buttons found, try dropdown
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, question_id))
                    )
                    
                    if element.tag_name == 'select':
                        print("Handling as dropdown")
                        dropdown = Select(element)
                        for option in dropdown.options:
                            if option.text.strip() == answer.strip():
                                dropdown.select_by_value(option.get_attribute('value'))
                                print(f"Selected dropdown answer for {question_id}: {answer}")
                                break
                    else:
                        print(f"Unknown element type: {element.tag_name}")
                
            except Exception as e:
                print(f"Could not set answer for {question_id}: {str(e)}")
                print(f"Full error: {e.__class__.__name__}")
        
        # Optional: Wait for user confirmation before submitting
        input("Press Enter to submit quiz (or Ctrl+C to cancel)...")
        
        # Submit quiz
        submit_button = driver.find_element(By.ID, "submit_quiz_button")
        submit_button.click()
        
        # Wait for confirmation dialog and click submit
        confirm_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Submit Quiz')]"))
        )
        confirm_button.click()
        
        print("Quiz submitted successfully!")
        
    except Exception as e:
        print("Error during quiz submission:")
        print(str(e))
        raise e