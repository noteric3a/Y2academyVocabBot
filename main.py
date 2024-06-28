import pyautogui
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time

def take_screenshot():
    return

def chatgpt_response():
    return

def webscrape():
    # Setup the webdriver
    driver = webdriver.Chrome()

    # Open the website
    driver.get('https://y2academy.org/wp-login.php?redirect_to=https%3A%2F%2Fy2academy.org%2Fwp-admin%2Fadmin.php%3Fpage%3Ddsat_pt%26menu%3D34%26section_test%3D1%26section_id%3D4356&reauth=1')  # Replace with the actual URL

    username = "pl_eric chung_st"
    password = "pl0680524chu"

    # finding user and pass

    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_login')))

    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_pass')))

    # entering them in

    username_field.send_keys(username) 
    password_field.send_keys(password) 

    # filling stupid capatcha!!!!!
    # Locate the CAPTCHA equation text
    captcha_element = driver.find_element(By.XPATH, "//p[@class='c4wp-display-captcha-form']")

    # Extract the text from the CAPTCHA element
    captcha_text = captcha_element.text

    # remove and unneccessary texts
    parts = captcha_text.replace("Solve Captcha*", "").split()

    # Initialize variables
    first_number = None
    second_number = None
    third_number = None
    operator = None
    equal_sign = False
    solution = 0

    # Parse the parts to identify numbers and operator
    for part in parts:
        if part.isdigit():
            if first_number is None and operator is None:
                first_number = int(part)
            elif operator is not None and second_number is None and not equal_sign:
                second_number = int(part)
            else:
                third_number = int(part)
        elif part in ['+', '−', '×', '⁄']: # none of the characters are keyboard found characters!
            operator = part
        elif part == '=':
            equal_sign = True

    # Perform the calculation based on the identified operator and numbers
    if first_number is None:  # blank (operator) 1 = 1
        if operator == '+':
            solution = third_number - second_number
        elif operator == '−':
            solution = third_number + second_number
        elif operator == '×':
            solution = third_number / second_number
        elif operator == '⁄':
            solution = third_number * second_number
    elif second_number is None:  # 1 (operator) blank = 1
        if operator == '+':
            solution = third_number - first_number
        elif operator == '−':
            solution = first_number - third_number
        elif operator == '×':
            solution = third_number / first_number
        elif operator == '⁄':
            solution = first_number / third_number
    elif third_number is None:  # 1 (operator) 1 = blank
        if operator == '+':
            solution = first_number + second_number
        elif operator == '−':
            solution = first_number - second_number
        elif operator == '×':
            solution = first_number * second_number
        elif operator == '⁄':
            solution = first_number / second_number

    # Locate the input field for the CAPTCHA solution
    input_field = driver.find_element(By.ID, "c4wp_user_input_captcha")

    # Enter the solution into the input field
    input_field.send_keys(str(solution))

    # Submit the form if there's a submit button
    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'wp-submit')))
    submit_button.click()

    # LOGGED IN!!!

    # click the term and submit

    checkbox = driver.find_element(By.NAME, 'term_box')
    if not checkbox.is_selected():
        checkbox.click()

    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_condition_submit')))
    submit_button.click()

    # switch to popup window

    main_window = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main_window:
            popup_window = handle
            break

    driver.switch_to.window(popup_window)

    # WE'RE IN HAHAHAHHAHA

    time.sleep(5)
    # Find the link by id
    dsat_link = driver.find_element(By.ID, "toplevel_page_dsat_pt")
    # Click the link
    dsat_link.click()

    # get to the vocab section
    time.sleep(5)

    # Find the link by href
    dsat_vocab = driver.find_element(By.CSS_SELECTOR, "a[href='admin.php?page=dsat_vocab&vocab=1']")
    # Click the link
    dsat_vocab.click()

    # GOT PAST VOCAB PART HAHAHHAHAHAH

    

    time.sleep(100)

def main():
    webscrape()


main()