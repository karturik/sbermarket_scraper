from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import random
import requests
import threading
import re
import concurrent.futures

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


useragent = UserAgent()

# HTML CONTENT WRITE
def html_write(html: str, file_name: str) -> None:
    with open(f'category_pages/{file_name}.html', 'w', encoding='utf-8') as file:
        file.write(html)
        file.close()
        print(f'category_pages/{file_name}.html записан')

# GET LINKS TO REQUIRED CATEGORIES
def category_links_get() -> list[str]:
    with open('category_pages.txt', 'r', encoding='utf-8') as file:
        category_urls = file.read().strip().split('\n')
        return category_urls

# WRITE FINISHED LINKS
def done_page_write(category_page: str) -> None:
    with open('finished_pages.txt', 'a', encoding='utf-8') as file:
        file.write(category_page+'\n')
        file.close()

# GET LIST OF PROXIES
def ip_select() -> list[str]:
    proxy_list_update()
    with open('checked_proxies.txt', 'r', encoding='utf-8') as file:
        proxy_list = file.read().strip().split('\n')
        print(proxy_list)
        file.close()
    return proxy_list

# GET HTML OF CATEGORY PAGES
def start(proxy_list: list[str], category_page: str) -> None:
    proxy = random.choice(proxy_list)
    file_name = category_page.replace('/', '+').replace('?', '+').replace('.', '+').replace('%', '+')[34:]
    options = Options()
    options.add_argument(f"user-agent={useragent.random}")
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument("--window-size=1280,720")
    prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2,
                                                        'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                        'notifications': 2, 'auto_select_certificate': 2,
                                                        'fullscreen': 2,
                                                        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                        'media_stream_mic': 2, 'media_stream_camera': 2,
                                                        'protocol_handlers': 2,
                                                        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                        'metro_switch_to_desktop': 2,
                                                        'protected_media_identifier': 2, 'app_banner': 2,
                                                        'site_engagement': 2,
                                                        'durable_storage': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)
    try:
        driver.get(category_page)
        check_element = None
        try:
            check_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ddl_product_link")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(1, 5))
            html = driver.page_source
            html_write(html, file_name)
            print("Get HTML")
        except Exception as e:
            print('No product cards on page')
            print(e)
            html = driver.page_source
            if 'class="catalog-listing-hard-filter-state__title"' in str(html):
                raise NameError('Finish page')
            if 'sticky-element-wrapper' in str(html) and not 'catalog-listing__items catalog-listing__items_divider-wide' in str(html):
                raise NameError('Finish page')
            if 'catalog-listing-content' in str(html) and not 'catalog-item ddl_product' in str(html):
                raise NameError('Finish page')
            print('No check elements, try again')
            if 'ERR_PROXY_CONNECTION_FAILED' or 'ConnectTimeout' or 'id="challenge-running"' or 'ERR_TIMED_OUT' or 'Подозрительная активность' or 'ERR_TIMED_OUT' in html:
                raise NameError('Proxy dont work')
            start(proxy_list, category_page, file_name)
    except OSError as e:
        if 'ProxyError' or 'ERR_PROXY_CONNECTION_FAILED' in str(e):
            if len(proxy_list) != 1:
                print('Invalid proxy, try next')
                start(proxy_list, category_page, file_name)
            else:
                print('No working proxies, pars another')
                proxy_list = ip_select()
                start(proxy_list, category_page, file_name)
        if 'NameError' in str(type(e)):
            driver.close()
            raise NameError
        else:
            print(type(e).__name__, e.args)
            driver.close()
            raise NameError('ProxyError')


def main(category_pages: list[str]) -> None:
    for category_page in category_pages:
        proxy_tries = 0
        # print(category_urls)
        proxy_list = ip_select()
        i = 2
        file_name = '0'
        finish_page = False
        while i <= 1188 and finish_page == False:
            finish_page = False
            success = 'No'
            while success != 'Yes':
                success = 'No'
                try:
                    if not category_page in finished_pages:
                        print('Try page ', category_page)
                        start(proxy_list, category_page, file_name)
                        done_page_write(category_page)
                        time.sleep(3)
                        category_page = re.sub(r'page-(\d+)', f'page-{i}', category_page)
                        file_name = category_page
                        i+=1
                        proxy_tries = 0
                        success = 'Yes'
                    else:
                        print("Page already finished: ", category_page)
                        category_page = re.sub(r'page-(\d+)', f'page-{i}', category_page)
                        i += 1
                        success = 'Yes'
                except Exception as e:
                    print('Error', e)
                    if not 'Finish page' in str(e):
                        # pass
                        proxy = proxy_list[0]
                        proxy_tries += 1
                        print('Try', proxy_tries, "/3")
                        time.sleep(random.randint(1,5))
                        if proxy_tries == 3:
                            proxy_list.remove(proxy)
                            print('Proxy deleted, left ', len(proxy_list))
                            proxy_tries = 0
                    else:
                        print('Last page!')
                        finish_page = True
                        success = 'Yes'

# PARSE PROXY LIST
def proxy_list_update():
    def site_proxies_scrap(url: str) -> None:
        r = requests.get(url)
        print('Connect to ip page', url)
        soup = BeautifulSoup(r.content, features="html.parser")
        text_field = soup.find('textarea', class_="form-control").text
        ls = text_field.split("\n")
        ls_1 = ls[3:-1]
        with open("unchecked_proxies.txt", 'a', encoding="utf-8") as file:
            for i in ls_1:
                file.write(i + "\n")
            file.close()


    def doubler(proxy: str) -> None:
        with open('checked_proxies.txt', 'a', encoding='utf-8') as file:
            try:
                page = requests.get('https://ipecho.net/plain', timeout=3, proxies={"http": proxy, "https": proxy})
                file.write(proxy + '\n')
                print('Status OK: ', proxy)
            except OSError as e:
                pass
                print('Dont work:', proxy)
                # print(type(e).__name__, e.args, proxy)


    with open('checked_proxies.txt', 'w', encoding='utf-8') as file:
        file.close()
    with open('unchecked_proxies.txt', 'w', encoding='utf-8') as file:
        file.close()
    site_proxies_scrap("https://www.sslproxies.org/")
    site_proxies_scrap("https://free-proxy-list.net/#list")
    site_proxies_scrap("https://free-proxy-list.net/anonymous-proxy.html")
    # site_proxies_scrap("https://api.proxyscrape.com/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")

    with open('unchecked_proxies.txt', 'r', encoding='utf-8') as file:
        proxies = file.read().split("\n")
        file.close()
    for proxy in proxies:
        try:
            my_thread = threading.Thread(target=doubler, args=(proxy,))
            my_thread.start()
        except:
            time.sleep(3)
            my_thread = threading.Thread(target=doubler, args=(proxy,))
            my_thread.start()


if __name__ == '__main__':
    try:
        with open('finished_pages.txt', 'r', encoding='utf-8') as file:
            finished_pages = file.read().split('\n')
            file.close()
    except:
        with open('category_pages/finished_pages.txt', 'a', encoding='utf-8') as file:
            file.close()
            finished_pages = ""
    category_urls = category_links_get()
    proxy_list = ip_select()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(main, (category_urls, proxy_list))

