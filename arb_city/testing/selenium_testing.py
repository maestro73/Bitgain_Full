#https://public.bitmex.com/?prefix=data/trade/

from selenium import webdriver
import time

# To prevent download dialog
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', '/tmp')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

browser = webdriver.Chrome()
browser.get("https://public.bitmex.com/?prefix=data/trade/")
time.sleep(5)
browser.find_element_by_link_text("20190726.csv.gz").click()