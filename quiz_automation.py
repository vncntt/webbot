import os
import re
import sys
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import parse_html
import get_answers
import submit_answers
from dotenv import load_dotenv

load_dotenv()

def extract_quiz_id(url):
    """Extract quiz ID from Canvas URL"""
    parsed = urlparse(url)
    path_parts = parsed.path.split('/')
    return path_parts[path_parts.index('quizzes') + 1]

def setup_quiz_directory(quiz_id):
    """Create and return path to quiz directory"""
    dir_path = f'quiz_{quiz_id}'
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def get_initial_source(driver, url, quiz_dir):
    """Get initial quiz page source and save it"""
    driver.get(url)
    
    take_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Take the Quiz Again')] | //a[contains(text(), 'Take the Quiz Again')] | //button[contains(text(), 'Resume Quiz')] | //a[contains(text(), 'Resume Quiz')] | //button[contains(text(), 'Take the Quiz')] | //a[contains(text(), 'Take the Quiz')]"))
    )
    take_button.click()

    source_path = os.path.join(quiz_dir, 'quiz_source.html')
    with open(source_path, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    
    return source_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python quiz_automation.py <quiz_url>")
        sys.exit(1)

    quiz_url = sys.argv[1]
    quiz_id = extract_quiz_id(quiz_url)
    quiz_dir = setup_quiz_directory(quiz_id)
    
    # Define expected file paths
    source_path = os.path.join(quiz_dir, 'quiz_source.html')
    json_path = os.path.join(quiz_dir, 'quiz_structure.json')
    
    # Create single WebDriver instance
    driver = webdriver.Chrome()
    try:
        # Initial login
        print("Logging into Canvas...")
        driver.get("https://canvas.ucsd.edu")
        username = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ssousername"))
        )
        password = driver.find_element(By.ID, "ssopassword")
        
        username.send_keys(os.environ["CANVAS_USERNAME"])
        password.send_keys(os.environ["CANVAS_PASSWORD"])
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        print("Waiting for Duo push confirmation...")
        WebDriverWait(driver, 30).until(
            lambda x: "canvas.ucsd.edu" in x.current_url
        )
        
        # Step 1: Check if source exists
        if os.path.exists(source_path):
            print("Step 1: Quiz source already exists, skipping...")
        else:
            print("Step 1: Getting quiz source...")
            source_path = get_initial_source(driver, quiz_url, quiz_dir)
        
        # Step 2: Check if structure exists
        if os.path.exists(json_path):
            print("Step 2: Quiz structure already exists, skipping...")
        else:
            print("Step 2: Parsing quiz structure...")
            parse_html.parse_quiz_structure(source_path)
        
        print("Step 3: Finding correct answers...")
        get_answers.canvas_automation(driver, quiz_dir, quiz_url)
        
        print("Step 4: Submitting final answers...")
        submit_answers.submit_final_answers(driver, quiz_dir, quiz_url)
        
        print(f"\nWorkflow complete! Check {quiz_dir} for results.")
        
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()