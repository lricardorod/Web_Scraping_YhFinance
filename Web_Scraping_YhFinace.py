#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.ui as ui
import time
from selenium.webdriver.support import expected_conditions as EC
from IPython.display import display


# In[2]:


# It is important to explain the methodology before I begin. The link provided to access Yahoo Finance wasn't 
# returning any data, so I had to do a workaround that. Instead of gathering all data from one web page I had to 
# acess individual Ticker pages, and then extract the necessary data from each one. It is also good to mention 
# none of them had the 'Net Borrowings' field, nevertheless the implementation is on the code.


# In[3]:


# I organized the program into functions so it would be easier to change necessary bugs and implement new code

# The fist function logs into the desired web page and clicks the necessary buttons
def geturl(url):
    
    # Defined the two buttons I needed to click as constants
    # The fisrt button sets the period of view to quarters, such as intended
    Quart_but = 'button[class="P(0px) M(0px) C($linkColor) Bd(0px) O(n)"]'
    # The second button expands the view, so we can gather all possible and necessary data
    exp_but = 'button[class="expandPf Fz(s) Bd(0) C($linkColor) C($linkActiveColor):h Fw(500) D(n)--print Fl(end) Mt(5px)"]'
    
    # Using 'wait' to wait for the page to load
    wait = ui.WebDriverWait(driver,10)
    driver.get(url)
    # 'time.sleep' and 'wait' because the pages were loading too quickly to click the buttons
    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, Quart_but))).click()
    # wait to click the second button
    wait.until(lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=exp_but))
    driver.find_element(by=By.CSS_SELECTOR, value=exp_but).click()

# The second function converts the html code into a Dataframe  
def convhtml(url):
    
    # First I used the 'geturl' function
    geturl(url)
    time.sleep(1)
    content = driver.page_source
    # Utilized soup to find the content/elements
    soup = BeautifulSoup(content)
    features = soup.find_all('div', class_='D(tbr)')
    # Finaly utilized de 'createDF' function to convert the html to a DataFrame
    df = createDF(features)
    
    return df


# This function filters the html obtained from 'features' and rearranges it into a pandas DataFrame
def createDF(features):
    
    headers = []
    temp_list = []
    label_list = []
    final = []
    index = 0
    #create headers
    for item in features[0].find_all('div', class_='D(ib)'):
        headers.append(item.text)
    #statement contents
    while index <= len(features)-1:
        #filter for each line of the statement
        temp = features[index].find_all('div', class_='D(tbc)')
        for line in temp:
            #each item adding to a temporary list
            temp_list.append(line.text)
        #temp_list added to final list
        final.append(temp_list)
        #clear temp_list
        temp_list = []
        index+=1
    df = pd.DataFrame(final[1:])
    df.columns = headers
    
    return df 

# This function cleans the Dataframe to the data we need. This whole code was designed so this function is the only
# thing we need to change in future implementations. I gathered all data from the website so that we don't need to
# be searching for html code in the future. We already have all data, we only need to clean it to whatever is desired.
def cleanDF(df1,df2,df3):
    
    df1 = df1.drop(columns='ttm')
    df3 = df3.drop(columns='ttm')
    
    # So, I filtered the fields requested and saved them into a new Dataframe
    finaldf=df1.loc[df1['Breakdown']=='Operating Income']
    interdf=df3.loc[df3['Breakdown']=='Net Income from Continuing Operations']
    finaldf = finaldf.append(interdf)
    interdf=df2.loc[df2['Breakdown']=='Retained Earnings']
    finaldf = finaldf.append(interdf)
    interdf=df3.loc[df3['Breakdown']=='Changes in Cash']
    finaldf = finaldf.append(interdf)
    interdf=df3.loc[df3['Breakdown']=='Net Borrowings']
    finaldf = finaldf.append(interdf)

    finaldf = finaldf.reset_index(drop=True)
    
    return finaldf


# This function utilizes 'convhtml' to generate three Dataframes: one from the financials, one from the balance 
# sheet and one from the cash flow. I only needed the Ticker as a parameter to access all the diferent financial
# pages from diffent Tickers.
def getDF(Ticker):
    
    url1 = "https://finance.yahoo.com/quote/{}/financials?p={}".format(Ticker,Ticker)
    url2 = 'https://finance.yahoo.com/quote/{}/balance-sheet?p={}'.format(Ticker,Ticker)
    url3 = 'https://finance.yahoo.com/quote/{}/cash-flow?p={}'.format(Ticker,Ticker)
    
    df1 = convhtml(url1)
    df2 = convhtml(url2)
    df3 = convhtml(url3)
    
    # The 'cleanDF' function unifies the three DataFrames into one, besides filtering the necessary data.
    df = cleanDF(df1,df2,df3)
    
    return df

# the 'getTicker' function asks the user to input the Tickers needed.
def getTicker():
    ticker_input = input('Name the Tickers you want to get Data from, separated by commas and without spaces: ')
    #I put all the Tickers into a list so I can iterate through them in the main function.
    ticker_input = ticker_input.split(',')
    Tickers = [i.upper() for i in ticker_input]
    return Tickers

# This is the main function, where all the process is handled, from getting the data needed to formatig it
# as requested
def main(Tickers,driver):
    
    newdf=pd.DataFrame()
    
    for Ticker in Tickers:
        # I get a Dataframe with all the data needed, one Ticker at a time.
        print('Getting {} ...'.format(Ticker))
        df = getDF(Ticker)
        column = df.columns
        # I iterate through the Dataframe so I can rearrange the data as requested.
        for b in range(len(df)):
            for j in range(1,5):
                # I generate and append one row at a time into a new Dataframe with the requested format.
                data = [(Ticker,df['Breakdown'][b],df[column[j]][b],column[j],'03/25/2022')]
                newdf = newdf.append(data)
    driver.quit()
    
    # I Rename the columns and reset the index.
    newdf = newdf.rename(columns={0: 'Ticker', 1: 'Field', 2: 'Value', 3: 'End Date', 4: 'Scrape Date'})
    newdf = newdf.reset_index(drop=True)
    print('The DataFrame looks like:')
    display(newdf)
    
    # Finally save it into a csv for the data science team to use and ask the user to name it.
    x = input('Name the csv file to be generated:')
    newdf.to_csv('{}.csv'.format(x),index=False)
    
    


# In[4]:


# Firstly we get the Ticker names
Tickers = getTicker()

# Then we choose and initiate wich webdriver would be utilized. I used Safari because I'm using a mac and i think
#  it perfmorms the best, but it should work on chrome or firefox as well.
# Cr_path = "/Users/ricardo/Downloads/chromedriver"
driver = webdriver.Safari()

main(Tickers,driver)


# In[ ]:




