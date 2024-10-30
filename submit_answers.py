import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_answers(file_path):
    answers = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                # Remove "Question " prefix and split on first colon
                line = line.replace("Question ", "")
                question_id, answer = line.strip().split(": ", 1)
                answers[question_id] = answer
    return answers

def submit_quiz_answers():
    driver = webdriver.Chrome()
    try:
        # Load answers
        answers = parse_answers('answers.txt')
        
        # Start with Canvas login page
        driver.get("https://canvas.ucsd.edu")
        
        # Wait for and handle SSO login
        username = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ssousername"))
        )
        password = driver.find_element(By.ID, "ssopassword")
        
        # Input credentials
        username.send_keys(os.environ["CANVAS_USERNAME"])
        password.send_keys(os.environ["CANVAS_PASSWORD"])
        
        print("Clicking login button...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        print("Waiting for Duo push confirmation...")
        time.sleep(15)  # Wait for manual Duo confirmation
        
        # Navigate to quiz page
        quiz_url = "https://canvas.ucsd.edu/courses/58515/quizzes/187173"
        print(f"Navigating to quiz page: {quiz_url}")
        driver.get(quiz_url)
        
        # Click "Take Quiz Again" button if present
        retake_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Take the Quiz Again')] | //a[contains(text(), 'Take the Quiz Again')] | //button[contains(text(), 'Resume Quiz')] | //a[contains(text(), 'Resume Quiz')]"))
        )
        retake_button.click()
        
        # Wait for quiz form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submit_quiz_form"))
        )
        
        # Fill in all answers at once
        for question_id, answer in answers.items():
            try:
                # Find dropdown by name
                dropdown_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, question_id))
                )
                dropdown = Select(dropdown_element)
                
                # Find and select the matching option
                for option in dropdown.options:
                    if option.text.strip() == answer.strip():
                        dropdown.select_by_value(option.get_attribute('value'))
                        print(f"Selected answer for {question_id}: {answer}")
                        break
                
            except Exception as e:
                print(f"Could not set answer for {question_id}: {str(e)}")
        
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
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    submit_quiz_answers() 