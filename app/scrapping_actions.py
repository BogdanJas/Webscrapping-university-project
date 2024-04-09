import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import app.database_actions as dba
from ApiRequest import request_to_openAI


def setup_webdriver():
    chrome_options = Options()
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    return driver, wait


async def twitter_scraping(data, user_id):
    driver, wait = setup_webdriver()
    driver.get(data['LinkToPost'])
    time.sleep(5)

    try:
        try_login(driver, wait, data)
        response_from_twitter, post_id = get_information_from_article(driver, wait)
        response_from_openAI = request_to_openAI(response_from_twitter)
        if response_from_openAI is not None: dba.insert_comment_information(response_from_openAI, post_id, user_id)
        print(response_from_openAI)
    except TimeoutException as e:
        print("Timeout occurred during Twitter login process.")
        driver.save_screenshot('debug_screenshot.png')
    finally:
        driver.quit()


def try_login(driver, wait, data):
    login_page = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="login"]')))
    login_page.click()

    username = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='text']")))
    username.send_keys(data['Login'])

    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
    next_button.click()

    password = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']")))
    password.send_keys(data['Password'])

    log_in = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="LoginForm_Login_Button"]')))
    log_in.click()
    time.sleep(5)


def check_image_presence(wait):
    try:
        first_article = wait.until(EC.element_to_be_clickable((By.XPATH, '(//article[@role="article"])[1]')))
        first_article.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetPhoto"] img')
        return True
    except NoSuchElementException:
        return False


def get_information_from_article(driver, wait):
    first_article = wait.until(EC.element_to_be_clickable((By.XPATH, '(//article[@role="article"])[1]')))
    tweet_text = first_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
    user_account = first_article.find_element(By.XPATH, ".//a[contains(@href, '/')]").get_attribute('href')
    has_image = check_image_presence(wait)

    if has_image:
        image = first_article.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetPhoto"] img').get_attribute('src')
    else:
        image = None

    post_time = first_article.find_element(By.CSS_SELECTOR, 'time[datetime]')
    datetime_value = post_time.get_attribute('datetime')
    date_only = datetime.fromisoformat(datetime_value).date()
    hour_only = datetime.fromisoformat(datetime_value).time()

    likes = first_article.find_element(By.CSS_SELECTOR, "div[data-testid='like'] span["
                                                        "data-testid='app-text-transition-container']").text
    bookmarks = first_article.find_element(By.CSS_SELECTOR, "div[data-testid='bookmark'] span["
                                                            "data-testid='app-text-transition-container']").text
    reposts = first_article.find_element(By.CSS_SELECTOR, "div[data-testid='retweet'] span["
                                                          "data-testid='app-text-transition-container']").text
    comments = first_article.find_element(By.CSS_SELECTOR, "div[data-testid='reply'] span["
                                                           "data-testid='app-text-transition-container']").text
    views = first_article.find_element(By.XPATH, ".//span[contains(., 'Views')]").text

    post_Id = dba.insert_post_information(user_account, tweet_text, has_image, image, comments,
                                          reposts, likes, views, bookmarks, date_only, hour_only)
    return tweet_text, post_Id


async def make_an_activity(user_id, action):
    user = dba.get_user_information(user_id)
    driver, wait = setup_webdriver()
    driver.get(user['LinkToPost'])
    time.sleep(5)

    try:
        try_login(driver, wait, user)
        first_article = wait.until(EC.element_to_be_clickable((By.XPATH, '(//article[@role="article"])[1]')))
        if action != 'retweet':
            action_button = first_article.find_element(By.CSS_SELECTOR, f"div[data-testid='{action}'] span["
                                                                        "data-testid='app-text-transition-container']")
        else:
            retweet_button = wait.until(EC.element_to_be_clickable(first_article.find_element(By.CSS_SELECTOR, f"div[data-testid='{action}'] span["
                                                                         "data-testid='app-text-transition-container']")))
            time.sleep(1)
            retweet_button.click()
            action_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='retweetConfirm']")
        action_button.click()
        return f'Post was {action}d'
    except TimeoutException as e:
        driver.save_screenshot('debug_screenshot.png')
        return "Timeout occurred during Twitter login process."
    except NoSuchElementException as e:
        driver.save_screenshot('debug_screenshot.png')
        return "The specified action had already been done."
    finally:
        driver.quit()


async def insert_comment(user_id):
    user = dba.get_user_information(user_id)
    driver, wait = setup_webdriver()
    driver.get(user['LinkToPost'])
    time.sleep(5)

    try:
        try_login(driver, wait, user)
        first_article = wait.until(EC.element_to_be_clickable((By.XPATH, '(//article[@role="article"])[1]')))
        wait.until(EC.element_to_be_clickable(first_article.find_element(By.CSS_SELECTOR, "div[data-testid='reply']"))).click()

        textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')))
        textarea.clear()
        textarea.send_keys(dba.get_comment(user_id))
        reply_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetButton"]')))
        reply_button.click()
        return "Comment was added"
    except TimeoutException:
        driver.save_screenshot('debug_screenshot.png')
        return "Error: Timed out waiting for page to load or element to become available."
    except NoSuchElementException:
        driver.save_screenshot('debug_screenshot.png')
        return "Error: The specified element could not be found."
    except Exception as e:
        driver.save_screenshot('debug_screenshot.png')
        return f"An unexpected error occurred: {e}"
    finally:
        driver.close()
