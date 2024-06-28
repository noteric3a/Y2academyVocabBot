import requests
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def chatgpt_response():
    api_key = "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"

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
                        "content": "You are an assistant that provides one-word answers from a given word list based on the provided definition.",
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Provide a one-word answer from the word list that best fits the definition in the image."
                            },
                            {
                                "type": "image_url",
                                "image_url": 
                                    {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                            }
                        ]
                    }
                ],
                "max_tokens": 7
            }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print("Answer: " + response.json()['choices'][0]['message']['content'])

    answer = response.json()['choices'][0]['message']['content']

    answer = answer.replace('*', '')
    answer = answer.replace('.', '')
    answer = answer.replace('"', '')
    answer = answer.replace("'", '')

    print("Cleaned answer: " + answer)
    
    return answer

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

    # Wait for the link by id to be present
    dsat_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "toplevel_page_dsat_pt")))

    # Create an instance of ActionChains
    actions = ActionChains(driver)

    # Hover over the first element
    actions.move_to_element(dsat_link).perform()

    # Wait for the hover effect to take place and the next element to be clickable
    dsat_vocab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='admin.php?page=dsat_vocab&vocab=1']")))

    # Click the second element
    dsat_vocab.click()

    # GOT PAST VOCAB PART HAHAHHAHAHAH

    time.sleep(5)
    
    # find tbody
    tbody = driver.find_element(By.TAG_NAME, 'tbody')

    # Find all tr elements within the tbody
    tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')

    # Initialize an empty list to store the tr elements
    tr_list = []

    # Loop through each tr element
    for tr in tr_elements:
        tds = tr.find_elements(By.TAG_NAME, 'td')  # Get all td elements within the tr
        if tds:  # Check if there are any td elements
            first_td = tds[0]  # Get the first td element
            try:
                # Check if the first td element contains an a element
                first_td.find_element(By.TAG_NAME, 'a')
                print(tr.text)
                # If it does, append the tr element to the list
                tr_list.append(tr)
            except:
                # If no a element is found, skip to the next tr element
                continue

    # now that we got each tr element with the respective tests, we can loop through them to do each one
    for test in tr_list:
        tds = test.find_elements(By.TAG_NAME, 'td')  # Get all td elements within the tr
        first_td = tds[0]  # Get the first td element
        aelement = first_td.find_element(By.TAG_NAME, 'a')
        aelement.click() # clicks this

        try:
            # confirms the test
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "simpleConfirm")))
            button.click()

            # confirm again
            yesbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm")))
            yesbutton.click()

            # in the memorization page 
            # confirming memorization complete
            memorybtn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "exam_1_passage_1")))
            memorybtn.click()

            # Find all elements with the ID "simpleConfirm"
            elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "simpleConfirm")))

            # Access the second element (index 1, since indexing starts from 0)
            button = elements[1]

            # I can now interact with the second element
            # WHY DO THEY HAVE 2 IDS FALSDABFSAF
            button.click()

            # confirming test ONCE AGAIN
            yesbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm")))
            yesbutton.click()
        except Exception as e:
            print(e)
            time.sleep(1000)

        answer_fields = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vocab_text')))
        next_button_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "buttons_div")))

        # LOOP FOR ALL 48 QUESTIONS
        for i in range(48):
            try:
                # Wait for some time between interactions
                time.sleep(2)
                driver.save_screenshot('screenshot.png')
                answer = chatgpt_response()

                # Get the specific element from the list
                answer_field = answer_fields[i]
                
                # Send keys to the input field
                answer_field.send_keys(answer)

                # Finding next button and clicking it
                if i < 48:
                    next_button_div = next_button_divs[i]
                    next_button = next_button_div.find_element(By.TAG_NAME, "input")
                    # Ensure the next button is visible and clickable
                    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_button))
                    
                    # Click the button
                    next_button.click()
                if i == 48:
                    submit_button = driver.find_element(By.CLASS_NAME, "last_save_btn")
                    # Ensure the next button is visible and clickable
                    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))
                    
                    # Click the button
                    submit_button.click()
            except Exception as e:
                print(e)
                time.sleep(1000)

        print("Test Complete.")
        time.sleep(10)

def main():
    webscrape()

main()