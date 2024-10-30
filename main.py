import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def load_quiz_structure():
    with open('quiz_structure.json', 'r') as f:
        return json.load(f)

def canvas_automation():
    driver = webdriver.Chrome()
    driver.get("https://canvas.ucsd.edu")
    quiz_structure = load_quiz_structure()
    
    try:
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
        
        # Navigate to specific quiz page
        quiz_url = "https://canvas.ucsd.edu/courses/58515/quizzes/187173?module_item_id=2443982"
        print(f"Navigating to quiz page: {quiz_url}")
        driver.get(quiz_url)

        # For each dropdown in the quiz
        for question in quiz_structure:
            if not question['id'] and not question['name']:  # Skip invalid entries
                continue
                
            dropdown_id = question['id'] or question['name']  # Use name if id is null
            print(f"\nTesting answers for dropdown: {dropdown_id}")
            
            # Try each option for this dropdown
            for option in question['options']:
                print(f"\nTrying option: {option['text']} (value={option['value']})")
                
                # Click "Take Quiz Again" button
                retake_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Take the Quiz Again')] | //a[contains(text(), 'Take the Quiz Again')]"))
                )
                retake_button.click()
                
                # Wait for quiz form to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "submit_quiz_form"))
                )
                
                # Select option from dropdown
                dropdown = Select(driver.find_element(By.ID, dropdown_id))
                dropdown.select_by_value(option['value'])
                
                # Submit quiz
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
                    
                    # Save to file
                    with open("answers.txt", "a") as f:
                        f.write(f"Question {dropdown_id}: {option['text']}\n")
                    
                    break  # Move to next dropdown
        
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print("Error during quiz interaction:")
        print(driver.page_source)
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    canvas_automation()
