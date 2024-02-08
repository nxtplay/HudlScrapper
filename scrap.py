from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image
import hashlib
import time
import pandas as pd
import os
# Path to your WebDriver executable
driver_path = '/opt/homebrew/bin/chromedriver'

# Instantiate a WebDriver
driver = webdriver.Chrome()

# URL of the login page
login_url = 'https://identity.hudl.com/login?state=hKFo2SBnQW43VXNsWVMzd0dWQmtZLWhJaUJzd1dYZXlKQzdEaaFupWxvZ2luo3RpZNkgVkkyN3ZlNmxubWhHbzV0NFZWWV90SVdXMm1pS09UcTijY2lk2SBuMTNSZmtIektvemFOeFdDNWRaUW9iZVdHZjRXalNuNQ&client=n13RfkHzKozaNxWC5dZQobeWGf4WjSn5&protocol=oauth2&response_type=id_token&redirect_uri=https%3A%2F%2Fwww.hudl.com%2Fapp%2Fusers%2Foidc%2Fcallback&scope=openid%20profile%20email&nonce=36BacphD%2FGOxYjwocY6V8zI7y6TeE533xMz%2BxQ9Alvc%3D&response_mode=form_post&screen_hint='

driver.get(login_url)

# Wait for the login fields to be present



# Wait for the dynamic content to load

# Initialize a DataFrame to store the data
column_mapping = {
    "HASH": "hash_col",
    "OFF FORM": "off_formation",
    "OFF STR": "off_str",
    "BACKFIELD": "backfield",
    "OFF PLAY": "off_play",
    "PLAY TYPE": "play_type",
    "PLAY DIR": "play_dir",
    "RESULT": "result",
    "GN/LS": "gn_ls",
    "EFF": "eff",
    "DEF FRONT": "def_front",
    "DEF STR": "def_str",
    "BLITZ": "blitz",
    "COVERAGE": "coverage",
    "QTR": "qtr",
    "DN": "dn",
    "video_path": "video_path"
}

i = 0
df_columns = list(column_mapping.values())
#df = pd.DataFrame(columns=['image_name', 'off_formation', 'off_play', 'off_play_type', 'play_res'])
#data_list =[]
df = pd.DataFrame(columns=df_columns)
ready = input("Are you ready to start? (y/n): ").lower()
if ready == 'n':
    driver.quit()
    exit()
previous_screenshot_name = ""
while True:
    
    all_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '.styles_cell__EuLNB.styles_isRowFocused__CNOtU.styles_isEditable__RAwyK')))
    
    row_data = {col: "" for col in df_columns}
    for element in all_elements:
        # ... Extract and store data ...
        data_qa_id = element.get_attribute('data-qa-id')
        if data_qa_id:
            # Extract the key part of the data-qa-id (before the dash)
            key = data_qa_id.split('-')[0]

            # Map to the DataFrame column and add to row data
            if key in column_mapping:
                row_data[column_mapping[key]] = element.text

        # Add the collected data as a new row in the DataFrame
        row_df = pd.DataFrame([row_data], columns=df_columns)  # Note the [row_data] - it creates a DataFrame with a single row
    # Prompt for frame adjustment and screenshot
    frame_input = input("Adjust the video to the right time and enter 's' for sideline, 't' for tight, 'e' for endzone: ").lower()
    if frame_input in ['s', 't', 'e']:
        # Take screenshot
        driver.save_screenshot('full_screenshot.png')
        image = Image.open('full_screenshot.png')
            
        width, height = image.size
        # Define the area to crop (x, y, width, height)
        print("Width: ", width, "Height: ", height)
        area_to_crop = (200, 100, width-900, height-420)  # Adjust this to the area you want
        cropped_image = image.crop((area_to_crop[0], area_to_crop[1], area_to_crop[0] + area_to_crop[2], area_to_crop[1] + area_to_crop[3]))
        
        if not previous_screenshot_name:
              # Hash the image contents
            image_bytes = cropped_image.tobytes()
            image_hash = hashlib.sha256(image_bytes).hexdigest()
       
            previous_screenshot_name = image_hash
            screenshot_name = f"sideline_{image_hash}.png"
        else:
            if frame_input == 's':
                screenshot_name = f"sideline_{previous_screenshot_name}.png"
            elif frame_input == 't':
                screenshot_name = f"tight_{previous_screenshot_name}.png"
            else:
                screenshot_name = f"endzone_{previous_screenshot_name}.png"
        directory = "photos/" + previous_screenshot_name
        if not os.path.exists(directory):
            os.makedirs(directory)
        url = directory +"/" + screenshot_name
        cropped_image.save(url)

    # Move to next item
    webdriver.ActionChains(driver).send_keys(Keys.RIGHT).perform()
    time.sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
    
    # Prompt for new clip or same play
    new_clip_input = input("Enter 'n' for a new clip or 'no' to stop or press Enter for the same play: ").lower()
    if new_clip_input == 'no':
        # Save current data to DataFrame
        row_data['video_path'] = previous_screenshot_name
        df = pd.concat([df, pd.DataFrame([row_data], columns=df_columns)], ignore_index=True)
        row_data = {col: "" for col in df_columns}  # Reset row data for new clip

        break
    if new_clip_input == 'n' or new_clip_input == 's':
        # Save current data to DataFrame
        print(i)
        i += 1
        row_data['video_path'] = previous_screenshot_name  # Assuming you have a column for video path
        df = pd.concat([df, pd.DataFrame([row_data], columns=df_columns)], ignore_index=True)
        row_data = {col: "" for col in df_columns}  # Reset row data for new clip
        previous_screenshot_name = ""
# Save the DataFrame to a CSV file
df.to_csv('screenshot_data.csv', index=False)

# Close the browser when done
driver.quit()
