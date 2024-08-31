"""
The way I have this code set up is that it iterates through a list of Aliyev
articles and filters out the articles that redirect to the main website, or that
have a 404 Error, or that don't have the keyword anywhere in the body of the
article, or that are otherwise invalid. If a website has the desired keyword,
the code adds the sentence with the keyword to the article's row in the resulting
spreadsheet.

A few general notes:
- The major limitation of this code is that it only searches for a direct keyword.
  If Aliyev alludes to Armenia and the keyword is Armenia, for example, the code
  won't pick up on it.
- This code takes a while to run, if you're updating the spreadsheet I recommend
  setting FIRST_INDEX to the last website on it and setting LAST_INDEX to the
  most recent article to save time and comptutation power, and then manually
  combining the two spreadsheets.
- This code assumes that articles will always be added to the website with a new,
  higher number at the end of their URL. If the Azeri government changes the way
  their website is set up, the code will no longer work because it assumes that
  the base URL is the same for all of the articles.

Things you need to have installed:
- Python 3
- requests
- pandas
- selenium
- Chrome
- chromedriver

 Output: out.csv, a file containing each article with the keyword's date, title,
         URL, and the text relating to the keyword

NOTE: As of now, the code is not working because of a Chrome update, but the logic
      should apply to other websites

Seran Goudsouzian, July-August 2023
"""

import requests
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import pandas
from pandas import DataFrame
import os.path

# THINGS YOU CAN CHANGE

FIRST_INDEX = 58371
# the start of the loop of websites, this number should correspond to the first
# website that you want to analyze- check the end of the URL

LAST_INDEX = 60572
# the end of the loop of websites, this number should correspond to the last
# website that you want to analyze- check the end of the URL

KEYWORD = "Armenia"
# the word you want to search for, case-sensitive

BASE_URL = "https://president.az/en/articles/view/"

# Initialization of df columns
dates = []
titles = []
urls = []
text = []

# Initialization of web scraper- this didn't work once Chrome updated

chrome_options = Options()
chrome_options.binary_location = "PATH TO CHROME"

browser = webdriver.Chrome(options=chrome_options, service=r'PATH TO CHROMDRIVER',)

# The main code
for i in range(FIRST_INDEX, LAST_INDEX+1):
    URL = BASE_URL + str(i)
    browser.get(URL)
    title = browser.title
    # Filters out websites that redirect or produce an error
    if(title == "Official web-site of President of Azerbaijan Republic") or \
    (title == "404 Not Found"):
        print("Website #" + str(i) + ": Not Found")
    elif((browser.find_element(by=By.XPATH, value='/html/body/div/div[1]/ul/li[2]/a')).text=='RECEIVED LETTERS'):
        print("Website #" + str(i) + ": Not an Aliyev statement")
    else:
        # results- the body of the article, found with the html executable path
        results = browser.find_element(by=By.XPATH, value='html/body/div/div[2]')
        body = results.text

        if(body.find(KEYWORD) == -1):
            print("Website #" + str(i) + ": No Keyword :(")

        # If website doesn't have punctuation, discount it bc it's probably
        # just a list of article titles
        elif((body.find(".") == -1) and (body.find("?") == -1) and (body.find("!") == -1)):
            print("Website #" + str(i) + ": Not an article")
        else: #If the article has the keyword, isolate the sentences with it and
              # add them to the .csv file
            string = ""
            while body.find(KEYWORD) != -1:
                arm_ind = body.find(KEYWORD)
                start_ind = arm_ind
                end_ind = arm_ind

                while ((body[start_ind] != ".") and (body[start_ind] != "\n") \
                and (body[start_ind] != "!") and (body[start_ind] != "?")):
                    start_ind = start_ind - 1

                while ((body[end_ind] != ".") and (body[end_ind] != "\n") and \
                (body[end_ind] != "!") and (body[end_ind] != "?")):
                    end_ind = end_ind + 1

                string += body[start_ind+1:end_ind+1]
                string += "\n"

                body = body[end_ind:]

            # Adding the columns to the dataframe
            dates.append((browser.find_element(by=By.XPATH, \
            value='/html/body/div/div[2]/div/div[1]/span')).text)
            titles.append(title)
            urls.append(URL)
            text.append(string)
            df = DataFrame({'Date/Time': dates, 'Title': titles, \
            'URL': urls, 'Text': text})

            # Exporting the .csv file
            df.to_csv('out.csv', index=False)

            print("Website #" + str(i) + ": Keyword Found!")
