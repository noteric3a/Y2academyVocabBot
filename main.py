import requests
import base64
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from PIL import Image
from io import BytesIO
import pytesseract
import time
import json
import os

api_key = ""
username = ""
password = ""

def encode_image(image_path):
    print("Encoding image...")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def chatgpt_response(input):
    print("Getting ChatGPT response...")

    base64_image = encode_image("screenshot.png")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that provides one-word answers from a given word list based on the provided definition."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{input}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 7
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    answer = response.json()['choices'][0]['message']['content']

    i = 0
    while ' ' in answer:
        if i < 3:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            answer = response.json()['choices'][0]['message']['content']
            i += 1
        else:
            break

    answer = answer.replace('*', '').replace('.', '').replace('"', '')
    print("Cleaned answer: " + answer)
    
    return answer

def log_answer(practice_test_name, question_number, answer):
    directory = "Vocab"
    file_name = f"{practice_test_name}_answers.txt"
    file_path = os.path.join(directory, file_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'a') as file:
        file.write(f"Question {question_number}: {answer}\n")

def read_answer(practice_test_name, question_number):
    directory = "Vocab"
    file_name = f"{practice_test_name}_answers.txt"
    file_path = os.path.join(directory, file_name)

    try:
        with open(file_path, "r") as file:
            for line in file:
                number, answer = line.strip().split(': ')
                questionnumber = int(number.split(" ")[1])
                if questionnumber == question_number:
                    return answer
            return "none"
    except FileNotFoundError:
        return "none"

def setup_driver():
    print("Setting up the webdriver...")
    driver = webdriver.Safari()
    return driver

def open_website(driver):
    print("Opening the website...")
    driver.get('https://y2academy.org/wp-login.php?redirect_to=https%3A%2F%2Fy2academy.org%2Fwp-admin%2Fadmin.php%3Fpage%3Ddsat_pt%26menu%3D34%26section_test%3D1%26section_id%3D4356&reauth=1')

def login(driver, username, password):
    print("Finding username and password fields...")
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_login')))
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_pass')))

    print("Entering username and password...")
    username_field.send_keys(username) 
    password_field.send_keys(password) 

def solve_captcha(driver):
    print("Filling CAPTCHA...")
    captcha_element = driver.find_element(By.XPATH, "//p[@class='c4wp-display-captcha-form']")
    captcha_text = captcha_element.text

    parts = captcha_text.replace("Solve Captcha*", "").split()

    first_number = None
    second_number = None
    third_number = None
    operator = None
    equal_sign = False
    solution = 0

    for part in parts:
        if part.isdigit():
            if first_number is None and operator is None:
                first_number = int(part)
            elif operator is not None and second_number is None and not equal_sign:
                second_number = int(part)
            else:
                third_number = int(part)
        elif part in ['+', '−', '×', '⁄']:
            operator = part
        elif part == '=':
            equal_sign = True

    if first_number is None:
        if operator == '+':
            solution = third_number - second_number
        elif operator == '−':
            solution = third_number + second_number
        elif operator == '×':
            solution = third_number / second_number
        elif operator == '⁄':
            solution = third_number * second_number
    elif second_number is None:
        if operator == '+':
            solution = third_number - first_number
        elif operator == '−':
            solution = first_number - third_number
        elif operator == '×':
            solution = third_number / first_number
        elif operator == '⁄':
            solution = first_number / third_number
    elif third_number is None:
        if operator == '+':
            solution = first_number + second_number
        elif operator == '−':
            solution = first_number - second_number
        elif operator == '×':
            solution = first_number * second_number
        elif operator == '⁄':
            solution = first_number / second_number

    print(f"CAPTCHA solution: {solution}")
    input_field = driver.find_element(By.ID, "c4wp_user_input_captcha")
    input_field.send_keys(str(solution))

    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'wp-submit')))
    submit_button.click()

    print("Logged in successfully!")

def accept_terms_and_conditions(driver):
    checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_box')))
    if not checkbox.is_selected():
        checkbox.click()

    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_condition_submit')))
    submit_button.click()

def find_answer_via_answerkey(answer_div):
    try:
        # finds the answer via this element which should look like this
        # <strong>The best answer is choice A.</strong>
        answer_element = answer_div.find_element(By.TAG_NAME, 'strong')
        answer = answer_element.text
        return answer[-2]
    except:
        try:
            # finds the answer via image input
            # looks like this: <img class="alignnone size-full wp-image-106976" src="http://y2academy.org/wp-content/uploads/2017/05/019.png" alt="01" width="327" height="307">
            img_element = answer_div.find_element(By.TAG_NAME, 'img')
            img_url = img_element.get_attribute('src')
            
            # Download the image
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            
            # Use OCR to extract text from the image
            answer_text = pytesseract.image_to_string(img)
            
            # Process the OCR output to find the answer
            # Assuming the OCR text contains "1. B" or similar format
            lines = answer_text.split('\n')
            for line in lines:
                if '.' in line:
                    # Extract the part after the dot and space
                    parts = line.split('.')
                    if len(parts) > 1:
                        answer = parts[1].strip()
                        if len(answer) == 1 and answer.isalpha():
                            return answer
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

def vocab():
    driver = setup_driver()
    open_website(driver)
    login(driver, username, password)
    solve_captcha(driver)
    accept_terms_and_conditions(driver)

    main_window = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main_window:
            popup_window = handle
            break

    driver.switch_to.window(popup_window)

    dsat_link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "toplevel_page_dsat_pt")))
    actions = ActionChains(driver)
    actions.move_to_element(dsat_link).perform()

    dsat_vocab = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_vocab&vocab=1']")))
    dsat_vocab.click()

    print("Navigated to DSAT vocab page...")

    time.sleep(5)
    
    tbody = driver.find_element(By.TAG_NAME, 'tbody')
    tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

    tr_list = []

    print("Finding tests not done yet...")
    for tr in tr_elements:
        tds = tr.find_elements(By.TAG_NAME, 'td')
        if tds:
            first_td = tds[0]
            try:
                first_td.find_element(By.TAG_NAME, 'a')
                print(first_td.text)
                tr_list.append(tr)
            except:
                continue

    print(f"Supposed to do test: {tr_list[0].text}") if (tr_list) else None
    print(f"Tests Left: {len(tr_list)}") if (tr_list) else print("Cant find any!")

    while tr_list:
        try:
            test_element = tr_list[0]
            tds = test_element.find_elements(By.TAG_NAME, 'td')
            first_td = tds[0]
            aelement = first_td.find_element(By.TAG_NAME, 'a')
            aelement.click()

            try:
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "simpleConfirm")))
                button.click()

                yesbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm")))
                yesbutton.click()

                memorybtn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "exam_1_passage_1")))
                memorybtn.click()

                elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "simpleConfirm")))
                button = elements[1]
                button.click()

                yesbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm")))
                yesbutton.click()
            except Exception as e:
                print(e)

            print("Starting test...")
            answer_fields = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vocab_text')))
            next_button_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "buttons_div")))
            
            test_names = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "test_section_name")))
            test_name = test_names[1].text
            print("Doing test: " + test_name)

            # check if there is a file for the test
            usegpt = False
            
            print(f"Does {test_name} have a file?")
            if read_answer(test_name, 1) == "none":
                print("Found file.")
                usegpt = True

            for i in range(len(answer_fields)):
                try:
                    print(f"Processing question {i + 1}...")
                    time.sleep(0.5)
                    driver.save_screenshot('screenshot.png')

                    # Method to find answers
                    answer_found = False
                    print("Finding Answer...")
                    if not usegpt:
                        answer = read_answer(test_name, i+1)
                        if answer == "none":
                            print("File found, no answer")
                            answer = chatgpt_response("Provide a one-word answer from the word list that best fits the definition in the image.")
                        else:
                            print("File found, Answer found.")
                            answer_found = True
                    else:
                        answer = chatgpt_response("Provide a one-word answer from the word list that best fits the definition in the image.")
                    
                    print(f"Answer: {answer}")

                    answer_field = answer_fields[i]
                    answer_field.send_keys(answer)

                    if not answer_found:
                        log_answer(test_name, i + 1, answer)

                    next_button_div = next_button_divs[i]
                    next_button = next_button_div.find_element(By.TAG_NAME, "input")
                    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_button))
                    next_button.click()
                    print("Moving on...")
                except Exception as e:
                    print(f"Error on question {i + 1}: Finished test?")
                    time.sleep(5)
                    submit_buttons = driver.find_elements(By.NAME, "exam_submit")
                    submit_button = submit_buttons[1]
                    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))

                    print("Submitting test...")
                    submit_button.click()
                    break

            print("Test Complete.")
            time.sleep(5)
        except selenium.common.exceptions.StaleElementReferenceException:
            print("Stale element reference exception encountered. Refreshing elements...")
            print("Finding tests not done yet...")
            tbody = driver.find_element(By.TAG_NAME, 'tbody')
            tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

            tr_list = []

            for tr in tr_elements:
                tds = tr.find_elements(By.TAG_NAME, 'td')
                if tds:
                    first_td = tds[0]
                    try:
                        first_td.find_element(By.TAG_NAME, 'a')
                        print(first_td.text)
                        tr_list.append(tr)
                    except:
                        continue

            print(f"Supposed to do test: {tr_list[0].text}") if (tr_list) else None
            continue
        
    print("Tests Finished.")
    driver.quit()

def ims():
    driver = setup_driver()
    open_website(driver)
    login(driver, username, password)
    solve_captcha(driver)
    accept_terms_and_conditions(driver)

    time.sleep(1)

    main_window = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main_window:
            popup_window = handle
            break

    driver.switch_to.window(popup_window)
    driver.set_window_size(1920, 1080)

    dsat_link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "toplevel_page_dsat_pt")))
    actions = ActionChains(driver)
    actions.move_to_element(dsat_link).perform()

    dsat_pt = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_pt']")))
    dsat_pt.click()

    print("Navigated to IMS page...")
    test_iterator = 0
    while True:
        # Locate the IMS Board elements
        datatable = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))
        tbody = datatable.find_element(By.TAG_NAME, 'tbody')
        tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

        a_element_ims = []
        for row in tr_elements:
            tds = row.find_elements(By.TAG_NAME, 'td')
            for td in tds:
                if td.text == 'IMS Board':
                    a_elements = td.find_elements(By.TAG_NAME, 'a')
                    if a_elements:
                        a_element_ims.extend(a_elements)

        if not a_element_ims:
            print("No more IMS Board elements found. Exiting...")
            break

        try:
            a_element = a_element_ims.pop(test_iterator)
            a_element.click()
            print("In the test section, now iterating through each section to see unfinished.")
        except IndexError:
            print("No more IMS Board elements found. Exiting...")
            break

        # Locate the test sections
        css_selector = '.imsboard_table.imsview'
        test_sections = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))

        section_iterator = 0
        while section_iterator < len(test_sections):
            test_sections_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tabs.tabs-style-linebox')))
            li_elements = WebDriverWait(test_sections_list, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'li')))
            driver.execute_script("arguments[0].click();", li_elements[section_iterator])

            # in the ims test page            
            test_sections = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))

            tbody = test_sections[section_iterator].find_element(By.TAG_NAME, 'tbody')
            test_tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

            test_tr_elements_list = []
            for test_tr_element in test_tr_elements:
                if "Undone" in test_tr_element.text:
                    test_tr_elements_list.append(test_tr_element)

            print(f"Doing tests now. {len(test_tr_elements_list)} to go. ") if len((test_tr_elements_list)) > 0 else print("No tests in this section...")

            # implement logic for doing the questions here
            while test_tr_elements_list:
                # we have to implement logic to not do finished ones
                element = test_tr_elements_list.pop(0)
                pw = element.find_element(By.CLASS_NAME, "ims_code_link")
                test_password = pw.text

                print(f"Test password: {test_password}")
                pw.click()

                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "simpleConfirm")))
                button.click()

                yesbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm")))
                yesbutton.click()

                pw_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "entered_password")))
                pw_input.send_keys(test_password)

                submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "test_password_submit")))
                submit_button.click()

                print("In the test now.")

                # finding the multiple choices, inputs, and answer keys
                question_displays = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'question_display')))
                multiple_choices = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'check_custom')))
                next_button_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "buttons_div")))
                math_inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "select")))
                print(f"Found {len(multiple_choices)} multiple choice, {len(next_button_divs)} buttons, and {len(math_inputs)} math inputs")

                # answer keys
                answer_keys = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ans_explain")))

                for i in range(len(question_displays)):
                    try:
                        print(f"Processing question {i + 1}...")
                        time.sleep(0.5)
                        # finding the answers
                        driver.save_screenshot('screenshot.png')

                        try:
                            answer = find_answer_via_answerkey(answer_keys[i])
                            print(f"Answer: {answer}")
                        except:
                            answer = chatgpt_response("Please read the text on the left side of the image and give a 1 letter answer for the question on the right side.")
                            print(f"Answer: {answer}")

                        # clicking the buttons
                        try:
                            multiple_choice_buttons = multiple_choices[i].find_elements(By.TAG_NAME, 'li')

                            if answer == "A":
                                multiple_choice_buttons[0].click()
                            if answer == "B":
                                multiple_choice_buttons[1].click()
                            if answer == "C":
                                multiple_choice_buttons[2].click()
                            else:
                                multiple_choice_buttons[3].click()
                        except:
                            math_select = math_inputs[i]
                            math_select_iterator = 0
                            for char in answer:
                                # iterating through each number in the answer
                                math_select[math_select_iterator].select_by_value(char)
                                math_select_iterator += 1

                        next_button_div = next_button_divs[i]
                        next_button = next_button_div.find_element(By.TAG_NAME, "input")
                        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_button))
                        next_button.click()
                        print("Moving on...")
                    except Exception as e:
                        print(f"Error on question {i + 1}: {e}. Finished test?")
                        submit_button = driver.find_element(By.CSS_SELECTOR, ".btn.last_save_btn")
                        submit_button.click()

                        print("Submitting test...")
                        time.sleep(5)
                        break

                # submitted the test, now going to main page and back to the tests

                print("Navigating back.")
                li_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wp-first-item.wp-has-submenu.wp-not-current-submenu.menu-top.menu-top-first.menu-icon-dashboard.menu-top-first")))
                dashboard = li_element.find_element(By.TAG_NAME, 'a')

                dashboard.click()
                print("Back at dashboard.")

                dsat_link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "toplevel_page_dsat_pt")))
                actions.move_to_element(dsat_link).perform()

                dsat_vocab = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_pt']")))
                dsat_vocab.click()

                # Locate the IMS Board elements
                datatable = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))
                tbody = datatable.find_element(By.TAG_NAME, 'tbody')
                tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

                a_element_ims2 = []

                # Iterate through each row in tr_elements
                for row in tr_elements:
                    tds = row.find_elements(By.TAG_NAME, 'td')
                    
                    # Iterate through each td in the row
                    for td in tds:
                        if td.text == 'IMS Board':
                            a_elements2 = td.find_elements(By.TAG_NAME, 'a')
                            
                            # Extend a_element_ims2 if a_elements2 is not empty
                            if a_elements2:
                                a_element_ims2.extend(a_elements2)

                # Check if a_element_ims2 is empty
                if not a_element_ims2:
                    print("No more IMS Board elements found. Exiting...")

                try:
                    # Iterate through a_element_ims2
                    a_element2 = a_element_ims2.pop(test_iterator)
                    a_element2.click()
                    print("In the test section, now iterating through each section to see unfinished.")
                except IndexError:
                    print("No more IMS Board elements found. Exiting...")
                print("Test Complete.")
                
                test_sections_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tabs.tabs-style-linebox')))
                li_elements = WebDriverWait(test_sections_list, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'li')))
                driver.execute_script("arguments[0].click();", li_elements[section_iterator])

                # in the ims test page            
                test_sections = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))

                tbody = test_sections[section_iterator].find_element(By.TAG_NAME, 'tbody')
                test_tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

                test_tr_elements_list = []
                for test_tr_element in test_tr_elements:
                    if "Undone" in test_tr_element.text:
                        test_tr_elements_list.append(test_tr_element)
                
            print("Tests finsihed.")
            section_iterator += 1
        print("Navigated to IMS page...")

        # going back to dashboard to loop again
        li_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wp-first-item.wp-has-submenu.wp-not-current-submenu.menu-top.menu-top-first.menu-icon-dashboard.menu-top-first")))
        dashboard = li_element.find_element(By.TAG_NAME, 'a')
        dashboard.click()
        print("Back at dashboard.")

        dsat_link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "toplevel_page_dsat_pt")))
        actions.move_to_element(dsat_link).perform()

        dsat_vocab = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_pt']")))
        dsat_vocab.click()
        test_iterator += 1

    # stops the bot
    print("Ending, there are no more tests")
    driver.quit()


def main():
    global api_key
    global username
    global password

    mode = input("Options: \n 1. Vocab (V) \n 2. IMS thing (I) \n Enter in an input: \n")

    with open("config.json", 'r') as file:
        config = json.load(file)

    api_key = config.get('gptkey', '')
    username = config.get('username', '')
    password = config.get('password', '')

    # Print the variables to verify
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'GPT Key: {api_key}')
    
    if mode == "V":
        vocab()
    elif mode == "I":
        ims()

if __name__ == "__main__":
    main()