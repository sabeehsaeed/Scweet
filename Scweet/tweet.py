from Scweet import utils
from time import sleep
import random
import json
from Scweet.utils import *
from selenium.webdriver.common.action_chains import ActionChains
from HLISA.hlisa_action_chains import HLISA_ActionChains



def log_user_page(user, driver, headless=True):
    sleep(random.uniform(1, 2))
    driver.get('https://twitter.com/' + user)
    sleep(random.uniform(1, 2))


def get_tweet_likers(username, id, headless, env, verbose=1, wait=2, limit=float('inf')):
    """ get the following or followers of a list of users """

    # initiate the driver
    print("Initializing Driver")
    driver = init_driver(headless=headless, env=env, firefox=True, option=["--window-position=0,0", "--window-size=1024,768"])
    sleep(wait)
    # log in (the .env file should contain the username and password)
    # driver.get('https://www.twitter.com/login')
    print("Logging in")
    log_in(driver, env, wait=wait)
    sleep(wait)
    # followers and following dict of each user

    # if the login fails, find the new log in button and log in again.
    if check_exists_by_link_text("Log in", driver):
        print("Login failed. Retry...")
        login = driver.find_element_by_link_text("Log in")
        sleep(random.uniform(wait - 0.5, wait + 0.5))
        driver.execute_script("arguments[0].click();", login)
        sleep(random.uniform(wait - 0.5, wait + 0.5))
        sleep(wait)
        log_in(driver, env)
        sleep(wait)
    # case 2
    if check_exists_by_xpath('//input[@name="session[username_or_email]"]', driver):
        print("Login failed. Retry...")
        sleep(wait)
        log_in(driver, env)
        sleep(wait)
    print(f"Going to likes for {username} - {id}")
    driver.get('https://twitter.com/' + username + '/status/' + id +"/likes")
    sleep(random.uniform(wait - 0.5, wait + 0.5))
    
    
    # check if we must keep scrolling
    scrolling = True
    primaryModal = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div')
    # last_position = driver.execute_script("return window.pageYOffset;")
    last_position = driver.execute_script("return arguments[0].scrollTop;", primaryModal)
    likers_elem = []
    likers_ids = set()
    is_limit = False
    wait = 0.5
    wait_margin = 0.1

    print("Crawling ")
    while scrolling and not is_limit:
        # get the card of following or followers
        # this is the primaryColumn attribute that contains both followings and followers
        
        # primaryColumn = driver.find_element(by=By.XPATH, value='//div[contains(@data-testid,"primaryColumn")]')
        # extract only the Usercell
        page_cards = primaryModal.find_elements(by=By.XPATH, value='//div[contains(@data-testid,"UserCell")]')
        for card in page_cards:
            # get the following or followers element
            element = card.find_element(by=By.XPATH, value='.//div[1]/div[1]/div[1]//a[1]')

            try:
                liker_elem = element.get_attribute('href')
            except Exception as e:
                sleep(random.uniform(wait - wait_margin, wait + wait_margin))
                print(repr(e))
                continue

            # append to the list
            liker_id = str(liker_elem)
            liker_elem = '@' + str(liker_elem).split('/')[-1]
            if liker_id not in likers_ids:
                likers_ids.add(liker_id)
                likers_elem.append(liker_elem)
            if len(likers_elem) >= limit:
                is_limit = True
                break
            if verbose:
                print(liker_elem)
        print("Found " + str(len(likers_elem)) + " " + "liking users")
        scroll_attempt = 0
        while not is_limit:
            sleep(random.uniform(wait - wait_margin, wait + wait_margin))
            driver.execute_script("arguments[0].scrollBy(0, window.innerHeight);", primaryModal)
            # driver.execute_script("arguments[0].scrollTo({ top: arguments[0].scrollHeight, behavior: 'smooth' });", primaryModal)
            
            
            
            # driver.execute_script("arguments[0].scrollBy({ top: window.innerHeight, behavior: 'smooth' });", primaryModal)
            # viewport_height = driver.execute_script("return window.innerHeight;")
            
            mouse_hover = random.randint(0,10)
            if(mouse_hover == 5):
                print("Mouse Move")
                actions = HLISA_ActionChains(driver)
                actions.move_to_element(primaryModal).perform()
            # actions.scroll_by(0,viewport_height, addDelayAfter=False, element=primaryModal).perform()
            
            # actions.move_by_offset(0, viewport_height).perform()
            
            # driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(random.uniform(wait - wait_margin, wait + wait_margin))
            # curr_position = driver.execute_script("return window.pageYOffset;")
            curr_position = driver.execute_script("return arguments[0].scrollTop;", primaryModal)
            if last_position == curr_position:
                scroll_attempt += 1
                print(f"Scroll Attempt {scroll_attempt}...")
                # end of scroll region
                if scroll_attempt >= 15:
                    scrolling = False
                    break
                else:
                    sleep(random.uniform(wait - wait_margin, wait + wait_margin))  # attempt another scroll
            else:
                last_position = curr_position
                break

    return likers_ids


def scrape_liking_users(username, tweet_id, env, verbose=1, headless=True, wait=2, limit=float('inf'), file_path=None):
    followers = get_tweet_likers(username, tweet_id, headless, env, verbose, wait=wait, limit=limit)

    # if file_path == None:
    #     file_path = 'outputs/' + str(users[0]) + '_' + str(users[-1]) + '_' + 'followers.json'
    # else:
    #     file_path = file_path + str(users[0]) + '_' + str(users[-1]) + '_' + 'followers.json'
    # with open(file_path, 'w') as f:
    #     json.dump(followers, f)
    #     print(f"file saved in {file_path}")
    return followers



def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
