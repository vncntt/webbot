import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_dropdown_selection():
    driver = webdriver.Chrome()
    try:
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
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Take the Quiz Again')] | //a[contains(text(), 'Take the Quiz Again')]"))
        )
        retake_button.click()
        
        # Wait for quiz form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submit_quiz_form"))
        )
        
        # Test specific dropdown from Question 2
        dropdown_name = "question_1813404_5ad018655f709bbc25f55df282068edb"  # First dropdown of Q2
        test_value = "8864"  # "Organ of Corti" option
        
        # Wait for dropdown to be present and interactable
        dropdown_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, dropdown_name))
        )
        
        # Create Select object and select value
        dropdown = Select(dropdown_element)
        dropdown.select_by_value(test_value)
        
        # Verify selection
        selected_option = dropdown.first_selected_option
        print(f"Selected option text: {selected_option.text}")
        print(f"Selected option value: {selected_option.get_attribute('value')}")
        
        input("Press Enter to close browser...")
        
    except Exception as e:
        print("Error during quiz interaction:")
        print(driver.page_source)
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    test_dropdown_selection() 