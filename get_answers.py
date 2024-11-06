import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv
import sys
load_dotenv()

def load_quiz_structure(quiz_dir):
    json_path = os.path.join(quiz_dir, 'quiz_structure.json')
    with open(json_path, 'r') as f:
        return json.load(f)

def save_answer(quiz_dir, question_name, answer_text):
    answers_path = os.path.join(quiz_dir, 'answers.txt')
    with open(answers_path, "a") as f:
        f.write(f"Question {question_name}: {answer_text}\n")

def try_answer(driver, question, option):
    """Try a single answer and return the score"""
    if question['type'] == 'multiple_choice':
        # Handle radio button selection
        radio = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"input[type='radio'][name='{question['name']}'][value='{option['value']}']"))
        )
        radio.click()
    else:
        # Handle dropdown selection
        dropdown_locator = (By.NAME if question['name'] else By.ID, question['name'] or question['id'])
        dropdown_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(dropdown_locator)
        )
        dropdown = Select(dropdown_element)
        dropdown.select_by_value(option['value'])

def canvas_automation(quiz_dir, quiz_url):
    driver = webdriver.Chrome()
    driver.get("https://canvas.ucsd.edu")
    quiz_structure = load_quiz_structure(quiz_dir)
    
    # Wait for SSO username field
    username = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ssousername"))
    )
    # Find password field
    password = driver.find_element(By.ID, "ssopassword")
    
    # Input credentials
    username.send_keys(os.environ["CANVAS_USERNAME"])
    password.send_keys(os.environ["CANVAS_PASSWORD"])
    
    print("Clicking login button...")
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    
    print("Waiting for Duo push confirmation...")
    time.sleep(15)  # Wait for manual Duo confirmation
    
    print(f"Navigating to quiz page: {quiz_url}")
    driver.get(quiz_url)
    
    # For each question in the quiz
    for question in quiz_structure:
        if not question.get('name'):
            continue
            
        print(f"\nTesting answers for question type {question['type']}: {question['name']}")
        
        # Try each option for this question
        for option in question['options']:
            print(f"\nTrying option: {option['text']} (value={option['value']})")
            
            # Click "Take Quiz Again" button or "Resume Quiz" button
            retake_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Take the Quiz Again')] | //a[contains(text(), 'Take the Quiz Again')] | //button[contains(text(), 'Resume Quiz')] | //a[contains(text(), 'Resume Quiz')]"))
            )
            retake_button.click()
            
            # Wait for quiz form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "submit_quiz_form"))
            )
            
            # Try the answer
            try_answer(driver, question, option)
            
            # Submit and check score
            submit_button = driver.find_element(By.ID, "submit_quiz_button")
            submit_button.click()
            
            # Handle confirmation popup
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            
            # Wait for results page to load and find score
            score_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "score_value"))
            )
            score = score_element.text.strip()
            print(f"Score: {score}")
            
            # If score is non-zero, we found a correct answer
            if score != "0":
                print(f"Found correct answer! {option['text']} gives score: {score}")
                save_answer(quiz_dir, question['name'], option['text'])
                break  # Move to next question
    
    input("Press Enter to close the browser...")
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <quiz_directory> <quiz_url>")
        sys.exit(1)
        
    quiz_dir = sys.argv[1]
    quiz_url = sys.argv[2]
    canvas_automation(quiz_dir, quiz_url)