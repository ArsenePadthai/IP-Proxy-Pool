If we want to use javascript website crawler, we need to install chrome binary and chromedriver

#### Download Chrome Headless
```
sudo apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb  # Might show "errors", fixed by next line
sudo apt-get install -f
```


#### Test If Chrome Is Correctly Installed
```
google-chrome --headless --remote-debugging-port=9222 https://chromium.org --disable-gpu
curl http://localhost:9222
```
If the html is returned correctly, then Chrome is installed correctly.


#### Download ChromeDriver
```
wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
```

set path
```
sudo vi ~/.profile
export PATH="$PATH:path_to_chromedriver"
source ~/.profile
```


#### Example Script
```
from  selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
client = webdriver.Chrome(chrome_options=chrome_options,executable_path='/home/wx/application/chromedriver')# 如果没有把chromedriver加入到PATH中，就需要指明路径
client.get("https://www.baidu.com")
content = client.page_source.encode('utf-8')
print (content)
client.quit()
```






## Blueprint
1. Learn more about python multi-processing
2. Modularize tester, filtering bad proxies before putting them into redis.
