from selenium import webdriver
import selenium.webdriver.support.ui as ui
from browsermobproxy import Server
import os
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import requests, json

# import time
# start = time.time()

server = Server(os.path.join(os.getcwd(), "venv/lib/site-packages/browsermob-proxy-2.1.4/bin/browsermob-proxy"))
server.start()
proxy = server.create_proxy()
options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=%s' % proxy.proxy)
options.add_argument('--headless')
options.add_argument('--mute-audio')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
driver = webdriver.Chrome(chrome_options=options)
wait = ui.WebDriverWait(driver, 10)

BASE_SEARCH_URL = "https://www.jiosaavn.com/search"
SONGS_URL = "/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

# Fetches the url from where the track is available
def load_track(title):
    link = ""
    try:
        url  = get_track_urls(title, 1) #The argument 1 specifies the number of items to fetch in the search results
        proxy.new_har()
        driver.get(url[0])
        wait.until(lambda driver: driver.find_element_by_css_selector("button.play"))
        play_home = driver.find_element_by_css_selector("button.play")
        play_home.click()
        time.sleep(8)
        link = find_url(proxy.har)
    except:
        pass

    return link

# Fetches the url and downloads the track
def download_track(title, artist, save_path):
    message = ""
    try:
        url = load_track(title + ' by ' + artist+'.mp3')
        audio = requests.get(url)
        fil = open(save_path, 'wb')
        fil.write(audio.content)
        message = "200: Downloaded the track successfully."
    except Exception as e:
        try:
            # print("\n-------\nError log:\n", e, '\n------')
            try:
                drive.close()
            except:
                pass
            url = load_track(title+' by '+artist)
            audio = requests.get(url)
            fil = open(save_path, 'wb')
            fil.write(audio.content)
            message = "200: Downloaded the track successfully."
        except:
            message = "404: Couldn't download this track."

    finally:
        try:
            server.stop()
            driver.close()
        except:
            pass
        finally:
            driver.quit()
 
        return message

def find_url(data):
    message="Not Done"
    for each in data['log']['entries']:
        try:
            if((each['response']['content']['mimeType']=='audio/mpeg')):
                print(each['request']['url'])
                return each['request']['url']
        except:
            continue
    return message

def get_track_urls(keyword, num):
    return search_songs(keyword, num)

def search_songs(keyword, num):
    url = BASE_SEARCH_URL+SONGS_URL+keyword
    songs = {}
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        songs = scrape_songs(soup, num)
    except:
        pass
    return songs

#Scraping to get the list of songs in search result
def scrape_songs(soup, num):
    songs = {}
    try:
        songs_soup = soup.find('ol', {'class': 'track-list song-search no-index'})
        containers = songs_soup.select('li.song-wrap')
        count = len(containers)
        if(num<count):
            count = num
        for i in range(count):
            url  = containers[i].find('div', {'class': 'main'}).find('a')['href']
            songs[i] = url
    except:
        pass
    return songs


# print(download_track("awara", "salman ali", "./downloads/Awara"))
# print("\n\nTime taken:\n", time.time()-start)