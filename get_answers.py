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

def load_existing_answers(quiz_dir):
    """Load existing answers from answers.txt into a dictionary"""
    answers_path = os.path.join(quiz_dir, 'answers.txt')
    existing_answers = {}
    
    if os.path.exists(answers_path):
        with open(answers_path, 'r') as f:
            for line in f:
                if line.strip():
                    # Parse "Question question_name: answer_text"
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        question_name = parts[0].replace('Question ', '').strip()
                        answer_text = parts[1].strip()
                        existing_answers[question_name] = answer_text
    
    return existing_answers

def canvas_automation(driver, quiz_dir, quiz_url):
    """Modified to check existing answers and resume progress"""
    quiz_structure = load_quiz_structure(quiz_dir)
    existing_answers = load_existing_answers(quiz_dir)
    
    print(f"Found {len(existing_answers)} existing answers")
    print(f"Navigating to quiz page: {quiz_url}")
    driver.get(quiz_url)
    
    # For each question in the quiz
    for question in quiz_structure:
        if not question.get('name'):
            continue
            
        question_name = question['name']
        
        # Check if we already have the answer
        if question_name in existing_answers:
            print(f"\nSkipping question {question_name} - answer already found: {existing_answers[question_name]}")
            continue
            
        print(f"\nTesting answers for question type {question['type']}: {question_name}")
        
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
                save_answer(quiz_dir, question_name, option['text'])
                break  # Move to next question