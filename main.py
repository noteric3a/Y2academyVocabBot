import requests
import base64
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
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

def chatgpt_response():
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
                        "text": "Provide a one-word answer from the word list that best fits the definition in the image."
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

    print("Answer received: " + response.json()['choices'][0]['message']['content'])

    answer = response.json()['choices'][0]['message']['content']

    i = 0
    while ' ' in answer:
        if i < 3:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            print("Answer received: " + response.json()['choices'][0]['message']['content'])
            answer = response.json()['choices'][0]['message']['content']
            i += 1
        else:
            break

    answer = answer.replace('*', '')
    answer = answer.replace('.', '')
    answer = answer.replace('"', '')

    print("Cleaned answer: " + answer)
    
    return answer

def log_answer(practice_test_name, question_number, answer):
    file_name = f"{practice_test_name}_answers.txt"
    with open(file_name, 'a') as file:
        file.write(f"Question {question_number}: {answer}\n")

def read_answer(practice_test_name, question_number):
    filename = f"{practice_test_name}_answers.txt"
    print(f"Filename: {filename}")
    print(f"Finding Question: {str(question_number)}")
    # checking if file exists
    try:
        with open(filename, "r+") as file:
            print("File Found!")
            for line in file:
                number, answer = line.strip().split(': ')
                questionnumber = int(number.split(" ")[1])
                if questionnumber == question_number:
                    print(f"Question: {str(questionnumber)}")
                    return answer
            return "none"
    except:
        return "none"

def webscrape():
    print("Setting up the webdriver...")
    driver = webdriver.Safari()

    print("Opening the website...")
    driver.get('https://y2academy.org/wp-login.php?redirect_to=https%3A%2F%2Fy2academy.org%2Fwp-admin%2Fadmin.php%3Fpage%3Ddsat_pt%26menu%3D34%26section_test%3D1%26section_id%3D4356&reauth=1')

    print("Finding username and password fields...")
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_login')))
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_pass')))

    print("Entering username and password...")
    username_field.send_keys(username) 
    password_field.send_keys(password) 

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

    checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_box')))
    if not checkbox.is_selected():
        checkbox.click()

    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_condition_submit')))
    submit_button.click()

    time.sleep(5)

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
    
    tbody = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
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
                            answer = chatgpt_response()
                        else:
                            print("File found, Answer found.")
                            answer_found = True
                    else:
                        answer = chatgpt_response()
                    
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
    print("Setting up the webdriver...")
    driver = webdriver.Safari()

    print("Opening the website...")
    driver.get('https://y2academy.org/wp-login.php?redirect_to=https%3A%2F%2Fy2academy.org%2Fwp-admin%2Fadmin.php%3Fpage%3Ddsat_pt%26menu%3D34%26section_test%3D1%26section_id%3D4356&reauth=1')

    print("Finding username and password fields...")
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_login')))
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_pass')))

    print("Entering username and password...")
    username_field.send_keys(username) 
    password_field.send_keys(password) 

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

    checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_box')))
    if not checkbox.is_selected():
        checkbox.click()

    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'term_condition_submit')))
    submit_button.click()

    time.sleep(3)

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

    dsat_vocab = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_pt']")))
    dsat_vocab.click()

    print("Navigated to IMS page...")

    datatable = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))
    print("Found the tests.")

    tbody = datatable.find_element(By.TAG_NAME, 'tbody')

    tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

    a_element_ims = []

    for row in tr_elements:
        tds = row.find_elements(By.TAG_NAME, 'td')
        for td in tds:
            if td.text == 'IMS Board':
                a_elements = td.find_elements(By.TAG_NAME, 'a')
                if a_elements:
                    print("Found 'a' element in 'IMS Board' td.")
                    a_element_ims.extend(a_elements)
    
    iterating = 0
    # in the loop of tests
    while a_element_ims:
        a_element = a_element_ims[0]
        a_element.click()
        print("In the test section, now iterating through each section to see unfinished.")
        # inside of the ims board page

        # you are now inside of the S1M1 of reading, iterate through each test and find which ones are undone
        css_selector = '.imsboard_table.imsview'
        
        # Wait until the element is found or timeout after 10 seconds
        test_sections = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
        
        # goal is to go through each section, do each test, get back to the same page, then check again for the undone tests until empty
        while iterating < len(test_sections):

            # find the tests undone
            tbody = test_sections[iterating].find_element(By.TAG_NAME, 'tbody')
            test_tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

            test_tr_elements_list = []

            for test_tr_element in test_tr_elements:
                if "Undone" in test_tr_element.text:
                    test_tr_elements_list.append(test_tr_element)

            print(f"Doing tests now. {str(len(test_tr_elements_list))} to go. ")

            # we are now doing tests until this list is empty
            while test_tr_elements_list:
                element = test_tr_elements_list[0]
                pw = element.find_element(By.CLASS_NAME, "ims_code_link")
                test_password = pw.text

                print(f"Test password: {test_password}")

                # in the test
                pw.click()

                # confirming the test and entering password
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "simpleConfirm")))
                button.click()

                yesbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm")))
                yesbutton.click()

                pw_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "entered_password")))
                pw_input.send_keys(test_password)

                submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "test_password_submit")))
                submit_button.click()

                print("In the test now.")

                # doing questions, inside test now

                multiple_choices = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'check_custom')))
                next_button_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "buttons_div")))
                print(f"Found {str(len(multiple_choices))} multiple choice and {str(len(next_button_divs))} buttons")

                for i in range(len(multiple_choices)):
                    try:
                        print(f"Processing question {i + 1}...")
                        time.sleep(0.5)
                        driver.save_screenshot('screenshot.png')

                        answer = 3#chatgpt_response()
                        
                        print(f"Answer: {answer}")
                        
                        """answer_field = answer_fields[i]
                        answer_field.send_keys(answer)"""

                        next_button_div = next_button_divs[i]
                        next_button = next_button_div.find_element(By.TAG_NAME, "input")
                        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_button))
                        next_button.click()
                        print("Moving on...")
                    except Exception as e:
                        print(f"Error on question {i + 1}: Finished test?")
                        submit_button = driver.find_element(By.CSS_SELECTOR, ".btn.last_save_btn")

                        print("Submitting test...")
                        print(submit_button.tag_name)
                        time.sleep(5)
                        break

                # sends us back to IMS page, so we need to renavigate
                print("Navigating back.")
                li_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wp-first-item.wp-has-submenu.wp-not-current-submenu.menu-top.menu-top-first.menu-icon-dashboard.menu-top-first")))
                dashboard = li_element.find_element(By.TAG_NAME, 'a')

                dashboard.click()
                print("Back at dashboard.")

                dsat_link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "toplevel_page_dsat_pt")))
                actions = ActionChains(driver)
                actions.move_to_element(dsat_link).perform()

                dsat_vocab = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_pt']")))
                dsat_vocab.click()

                print("Test Complete.")
                print("Navigated to IMS page...")

                datatable = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))
                print("Found the tests.")

                tbody = datatable.find_element(By.TAG_NAME, 'tbody')

                tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

                a_element_ims = []

                for row in tr_elements:
                    tds = row.find_elements(By.TAG_NAME, 'td')
                    for td in tds:
                        if td.text == 'IMS Board':
                            a_elements = td.find_elements(By.TAG_NAME, 'a')
                            if a_elements:
                                print("Found 'a' element in 'IMS Board' td.")
                                a_element_ims.extend(a_elements)

                a_element = a_element_ims[0]
                # clicks the ims button, not sure why its not registering the click
                a_element.click()
                print("In the test section, now iterating through each section to see unfinished.")

                # you are now inside of the S1M1 of reading, iterate through each test and find which ones are undone
                css_selector = '.imsboard_table.imsview'
                
                # Wait until the element is found or timeout after 10 seconds
                test_sections = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
                
            #time.sleep(10000)
            iterating += 1





def main():
    global api_key
    global username
    global password

    with open("config.json", 'r') as file:
        config = json.load(file)

    api_key = config.get('gptkey', '')
    username = config.get('username', '')
    password = config.get('password', '')

    # Print the variables to verify
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'GPT Key: {api_key}')

    ims()

main()


