#!/usr/bin/python
###IMPORTS###
from bs4 import BeautifulSoup as bsp
import os
import sys
import pandas as pd
import numpy as np
import requests #Communicatrion with web
from selenium import webdriver # Dynamic scraping for JS websites
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import re
import csv
from dotenv import load_dotenv
from sys import stderr
from dataclasses import dataclass, asdict


###CLASSES###
class SimpleScraper():
    """
    ATTRS
    -----
    page    [str]   URL of the page for scraping
    page_response    [Response]  response object from the webpage
    soup    [BeautifulSoup] beautifulSoup object built from the page content
    """
    def __init__(self, page):
        self.__page = page
        self.__page_response = None
        self.__isScraped = False
        self.__soup = None
        self._set_soup_()
    
    @property
    def page(self):
        return self.__page
    
    @property
    def soup(self):
        return self.__soup

    def _set_soup_(self):
        """Try to connect to get response from web page and store data to atributes."""
        if not self.__isScraped:
            self.__isScraped = True
            try:
                self.__page_response = requests.get(self.__page)
            except Exception as e:
                print("Error during connection try: {}".format(e), file = sys.stderr)
                raise e
            self.__soup = bsp(self.__page_response.content, 'html.parser')
    
    def set_page(self, page):
        """Set page's URL and get its source and prepare soup."""
        self.__isScraped = False
        self.__page = page
        self._set_soup_()
    
    def scrape(self, tag, class_ = None, id_ = None, all_results = True, parent = None, get_text = True):
        """
        Scrape matching tags
        ARGS
        ----
        tag [str]   tag type
        class_  [str]   tag class
        all_results [bool]  return all results or first results
        parent [object]    if provided, then search only childs of given element
        get_text    [bool]  if True return text from tag. Otherwise return tag
        
        RETURN
        ------
        if all_results is True then return list of tags. Otherwise return single object.
        """
        if not self.__isScraped:
            self._set_soup_()
        #Set function args
        if class_ and id_:
            args = [tag, {'class' : class_, 'id' : id_}]
        elif class_:
            args = [tag, {'class' : class_}]
        elif id_:
            args = [tag, {'id' : id_}]
        else:
            args = [tag]
        print(args)
        #Scrape data
        if all_results:
            if parent:
                if get_text:
                    return [i.get_text() for i in parent.findChildren(*args)]
                else:
                    return [i for i in parent.findChildren(*args)]
            else:
                if get_text:
                    return [i.get_text() for i in self.__soup.find_all(*args)]
                else:
                    return [i for i in self.__soup.find_all(*args)]

        else:
            if parent:
                if get_text:
                    return parent.findChildren(*args)[0].get_text()
                else:
                    return parent.findChildren(*args)[0]
            else:
                if get_text:
                    return self.__soup.find(*args).get_text()
                else:
                    return self.__soup.find(*args)
    
    
    




class Scraper(SimpleScraper):
    """
    Scraper class using Selenium during scraping. It allows wait for loading js content
    
    Atrs
    ----
    __driver    Selenium Firefox Webdriver
    __page      [str]   URL address to a website
    __page_response [response object]   Response object
    __soup  [bs4]   beautiful soup object based on given URL
    """
    
    
    def __init__(self, page, timeout, proxy = None):
        """
        ARGS
        ----
        page    [str]   URL of the page for scraping
        timeout [int]   posiive integer representing max timeout for page content in seconds
        """
        options = Options()
        options.add_argument("--headless")
        if proxy:
            options.add_argument('--proxy-server={}'.format(proxy))
        self.__driver = webdriver.Firefox(options = options) 
        self.__page = page
        self.__page_response = None
        self.__isScraped = False
        self.__soup = None
        self.__timeout = timeout
        self.__proxy = proxy
        self._set_soup_()
    
    @property
    def page(self):
        return self.__page
    
    @property
    def timeout(self):
        return self.__timeout
    
    @property
    def proxy(self):
        return self.__proxy
    
    @property
    def soup(self):
        return self.__soup
    
    def _set_soup_(self):
        """
        Set soup, page response and driver. If __isScraped is True then ommit those actions.
        """
        if not self.__isScraped:
            self.__isScraped = True
            try:
                self.__driver.get(self.__page)
            except Exception as e:
                print("Error during connection try: {}".format(e), file = sys.stderr)
                raise e
            self.__page_response = self.__driver.page_source
            self.__soup = bsp(self.__page_response, 'html.parser')
    
    def set_page(self, page):
        """Set page's URL and get its source and prepare soup."""
        self.__isScraped = False
        self.__page = page
        self._set_soup_()
    
    def wait_for_elem(self, class_, verbose = False):
        """Wait for element with provided class name and then load page_src."""
        if verbose:
            print("Waiting for element {}...".format(class_))
        WebDriverWait(self.__driver, timeout = self.__timeout).until(lambda x: x.find_element(By.CLASS_NAME, class_))
        self.__page_response = self.__driver.page_source
        self.__soup = bsp(self.__page_response, 'html.parser')

    def scrape(self, tag, class_ = None, id_ = None, all_results = True, parent = None, get_text = True):
        """
        Scrape matching tags
        ARGS
        ----
        tag [str]   tag type
        class_  [str]   tag class
        all_results [bool]  return all results or first results
        parent [object]    if provided, then search only childs of given element
        get_text    [bool]  if True return text from tag. Otherwise return tag
        
        RETURN
        ------
        if all_results is True then return list of tags. Otherwise return single object.
        If attribute page_src is empty then return -1.
        """
        if not self.__isScraped:
            self._set_soup_()
        #Set function args
        if class_ and id_:
            args = [tag, {'class' : class_, 'id' : id_}]
        elif class_:
            args = [tag, {'class' : class_}]
        elif id_:
            args = [tag, {'id' : id_}]
        else:
            args = [tag]
        #Scrape data
        if all_results:
            if parent:
                if get_text:
                    return [i.get_text() for i in parent.findChildren(*args)]
                else:
                    return [i for i in parent.findChildren(*args)]
            else:
                if get_text:
                    return [i.get_text() for i in self.__soup.find_all(*args)]
                else:
                    return [i for i in self.__soup.find_all(*args)]

        else:
            if parent:
                if get_text:
                    return parent.findChildren(*args)[0].get_text()
                else:
                    return parent.findChildren(*args)[0]
            else:
                if get_text:
                    return self.__soup.find(*args).get_text()
                else:
                    return self.__soup.find(*args)
        
    def quit(self):
        """Close driver"""
        self.__driver.close()
        self.__driver.quit()

            

class JSONLWriter():
    def __init__(self, output_):
        self.output = output_
    
    def overwrite(self, input_):
        """Write to file. If flie already exists, then overwrite it."""
        with open(self.output, 'w') as f:
            writer = jsonlines.Writer(f)
            if isinstance(input_, dict):
                writer.write(input_)
            elif isinstance(input_, list):
                for line in input_:
                    writer.write(line)
            else:
                raise Exception("Expected dictionary or list of dictionaries.")


    def write(self, input_):
        """Write to file. If flie already exists, then append content."""
        with open(self.output, 'a') as f:
            writer = jsonlines.Writer(f)
            if isinstance(input_, dict):
                writer.write(input_)
            elif isinstance(input_, list):
                for line in input_:
                    writer.write(line)
            else:
                raise Exception("Expected dictionary or list of dictionaries.")

@dataclass
class Game():
    title : str
    players : str
    release : int
    tags : list
    age : str
    time : str
    category : str
    publisher : str
    description : str
    weight : float

    @staticmethod
    def extract_params(params_list) -> tuple:
        """
        Extract valid values from scraped paragraph with parameters
        """
        player = params_list[0][0]
        time = params_list[1][0]
        age = params_list[2][1]
        weight = float(params_list[3][2])
        return player, time, age, weight

    @staticmethod
    def get_title_and_release_date(scraper : Scraper) -> tuple:
        """
        Get title and release date from website.
        ARGS
        ----
        scraper [Scraper]   Scraper with proper URL address settled
        
        RETURN
        ------
        tuple of strings containing release date and title in the given order.

        """
        #Verify if the address is proper
        #TO DO
        #Get game title and release date
        title = scraper.scrape('div', class_ = "game-header-title-info", get_text = False)[1]
        title = scraper.scrape('h1', parent = title, get_text = True, all_results = False)
        title = re.sub( r'\t+', '' , title)
        #Get release date and cleare additional symbols
        release = re.findall(r"\(.+\)", title)[0]
        release = re.sub(r"[\(\)]", "", release)
        #Remove release date from
        title = re.sub(r" +\(\d+\) +", "", title)
        #Remove trailing spaces
        title = re.sub(r"^ +", "", title)
        return release, title

    @staticmethod
    def get_descriptions(scraper : Scraper) -> tuple:
        """
        Get short desription and longer paragraph
        ARGS
        ----
        scraper [Scraper]   Scraper with proper URL address settled
        
        RETURN
        ------
        tuple of strings containing short descroption and the longer one in the given order.
        """
        #Get short description
        short_desc = scraper.scrape('div', class_ = "game-header-title-container", get_text = False)[1]
        short_desc = scraper.scrape('p', parent = short_desc, all_results = False)
        #Remove trailing spaces and tabulations
        short_desc = re.sub(r'[\t ]+$', '', short_desc)
        # print(short_desc.get_text())
        # print(">>>", type(short_desc))
        # print(short_desc.find('p').get_text())
        # print(short_desc.findChildren('p')[0].get_text())
        # print(scraper.scrape("p", parent = short_desc, class_ = "ng-binding ng-scope"))
        # print(scraper.scrape("p", parent = short_desc))
        # print(scraper.scrape('p', parent = short_desc))
        # short_desc = scraper.scrape(
            # 'p',
            # parent = scraper.scrape('div', class_ = "game-header-title-info", get_text = False)[1]
        # )
        # print(short_desc)




        



###FUNCTIONS###
def main():
    #Load variables
    load_dotenv()
    #Set variables
    baseURL = os.getenv("BASE_URL")
    bggURL = os.getenv("CATEGORIES_URL")
    gamesURL = os.getenv("GAMES_URL")
    shopURL = os.getenv("SHOP_URL")
    TIMEOUT = os.getenv("TIMEOUT")
    PROXY = os.getenv("PROXY") or None
    pages = 2
    LIMIT = 2
    iter = 0
    games_links = []

    #Initialize scraper
    reqScraper = SimpleScraper(bggURL)

    #Get categories
    categories = reqScraper.scrape('a', parent = reqScraper.scrape('table', get_text = False, all_results = False))

    #Get games links
    for page_no in range(1, pages + 1):
        pageURL = gamesURL + "/" + str(page_no)
        reqScraper.set_page(pageURL)
        games_links.extend(
            reqScraper.scrape(
                'a',
                class_ = "primary",
                get_text = False,
                parent = reqScraper.scrape('table', id_ = "collectionitems", get_text = False, all_results = False)
            )
        )
    games_links = [ baseURL + link.get('href') for link in games_links]
    print(games_links)

    #Initialize scraper for dynamically filled webpage
    dynamic_scraper = Scraper(bggURL, timeout = TIMEOUT, proxy = PROXY)
    
    #Scrape data for games individually
    for link in games_links:
        # print(link)
        dynamic_scraper.set_page(link)
        
        #Get game parameters
        params = dynamic_scraper.scrape('div', class_ = "gameplay-item-primary", get_text = False)
        #Split paragraphs to single words
        params = [re.split(r'[\t ]+', par.get_text()) for par in params]
        #Remove empty elements
        params = [list(filter(lambda t: t != "", par)) for par in params]
        print(params)
        #Parse games parameters
        extracted_params = Game.extract_params(params)
        print(extracted_params)
        #Get release date and game title
        release, title = Game.get_title_and_release_date(dynamic_scraper)
        print(release, title)
        #Get description
        description = Game.get_descriptions(dynamic_scraper)

if __name__ == "__main__":
    # pass
    main()
    iter = 0
    #Load variables
    load_dotenv()

    # baseURL = os.getenv("BASE_URL")
    # bggURL = "https://boardgamegeek.com/browse/boardgamecategory"
    # gamesURL = os.getenv("GAMES_URL")
    # shopURL = os.getenv("SHOP_URL")
    # pages = 2
    # LIMIT = 3
    # iter = 0

    # ###VARIABLES###
    # games = pd.DataFrame(
    #     {"title" : [],
    #     "release" : [],
    #     "tags" : [],
    #     "age" : [],
    #     "time" : [],
    #     "category" : [],
    #     "publisher" : [],
    #     "description" : [],
    #     "players" : [],
    #     'price_warehouse': [],
    #     'price_sell': [],
    #     'price_borrow': []
    #     }
    # )
    # fail = False
    # err =None
    # tags = set()
    # vals = [
    #     5,
    #     10,
    #     15,
    #     20,
    #     30,
    #     10000
    # ]


    # try: 
    #     cats = requests.get(bggURL)

    #     soup = bsp(cats.content, 'html.parser')
    #     print(type(cats), type(soup))
    #     categories = soup.find('table')
    #     categories = [cat_.get_text() for cat_ in categories.findAll('a')]
    #     # print(categories)
    #     # Get games links
    #     games_links = []
    #     for page_no in range(1, pages + 1):#Pass (1,10)
    #         gamesPage = requests.get(gamesURL + "/" + str(page_no))
    #         gamesSoup = bsp(gamesPage.content, 'html.parser')
    #         gamesPage = gamesSoup.find('table', id = "collectionitems")
    #         games_links.extend(gamesPage.find_all("a", {"class" : "primary"}))
    #     # Prepare links
    #     games_links = [ baseURL + link.get('href') for link in games_links]
    #     #Scrap games details
    #     # Warning. Those webpages are filled dynamicly so you have to do it different way
    #     options = Options()
    #     options.add_argument("--headless")
    #     driver = webdriver.Firefox(options = options) 
    # except:
    #     print("Problem during scraping games list")
    #     sys.exit(1)

    # for link in games_links:
    #     # Try connection for every single link
    #     try:
    #     #Get page
    #         print(link)
    #         driver.get(link)
    #         page = driver.page_source
    #         page = bsp(page, 'html.parser')
    #         # Get game parameters
    #         params = page.find_all('div', {"class" : 'gameplay-item-primary'})
    #         params = [re.split( r'[\t ]+', par.get_text()) for par in params]
    #         params = [list(filter(lambda t: t != "", par)) for par in params]
    #         players = params[0][0]
    #         time = params[1][0]
    #         age = params[2][1]
    #         # Get title 
    #         title = page.find_all('div', {"class" : "game-header-title-container"})[1]
    #         title = title.findChildren('div', {"class" : "game-header-title-info"})[0]
    #         title = re.sub( r'\t+', '' , title.findChildren('a')[0].get_text())
    #         #  Get release date
    #         release = re.sub( r'[\t()]+', '', page.find('span', {"class" : "game-year"}).get_text())
    #         # Get short description
    #         desc = page.find_all('div', {"class" : "game-header-title-container"})[1]
    #         # desc = re.sub( r'\W+', '', desc.find('p').get_text()) 
    #         desc = re.sub( r'\t+', '', desc.find('p').get_text()) 
    #         #Get tags and categoty
    #         details1 = [
    #             re.sub( r'\W+', '', feat.get_text())
    #             for feat in 
    #             page.find_all('div', {'class': 'feature-title'})[:2]
    #             ]
    #         cat_, tags_ = [
    #             re.findall(
    #                 '[A-Z][^A-Z]*',
    #                 re.sub( r'\W+', '', feat.get_text())
    #             )
    #             for feat in 
    #             page.find_all('div', {'class': 'feature-description'})[:2]
    #             ]
            
    #         for val in  ('N', 'A', "Viewpollandresults"):
    #             if val in cat_:
    #                 cat_.remove(val)
    #             if val in tags_:
    #                 tags_.remove(val)
    #         tags_[-1] = re.sub('[0-9]+more', '', tags_[-1])
    #         # Get publisher [TO FIX]
    #         publisher = page.find_all('div', {"class", "game-header-credits"})[1]
    #         if len(publisher.findChildren('li')) == 3:
    #             publisher = publisher.findChildren('li')[2]
    #         else:
    #             publisher = publisher.findChildren('li')[1]
    #         publisher = publisher.findChildren('a')[0].get_text()
    #         #Insert data to dictionary
    #         game = {
    #             "title" : title,
    #             "release" : release,
    #             "tags" : "###".join(tags_), 
    #             "age" : age,
    #             "time" : time,
    #             "category" : cat_[0],
    #             "publisher" : publisher,
    #             "description" : desc,
    #             "players" : players
    #         }
    #         # print(game)

    #         #Wyłuskanie ceny
    #         try:
    #             driver.get("https://www.google.com/search?q=" +
    #                 title +
    #                 "+gra+planszowa+ceneo"
    #             "Gry_planszowe;szukaj-" + title)
    #             page = driver.page_source
    #             page = bsp(page, 'html.parser')
    #             page = page.find('div', {"id" : 'res'})
    #             page = page.find('a', href = True)  
    #             print(page["href"])
    #             # Move to offers
    #             driver.get(page["href"])
    #             page = driver.page_source
    #             page = bsp(page, 'html.parser')
    #             prices = page.find_all('div', {"class" : "product-offer__product__price"})
    #             prices = [price.find('span', {"class" : "price"}).get_text() for price in prices]
    #             prices = [*map(lambda t: float(re.sub(',', '.', t)), prices)]
    #             prices.sort()
    #             # print(prices)
    #             if not len(prices):
    #                 med = 100000
    #                 sd = 0
    #             elif len(prices) % 2:
    #                 med = prices[len(prices) // 2]
    #                 sd = np.std(prices)
    #             else:
    #                 med = (prices[len(prices) // 2] + prices[len(prices) // 2 - 1]) / 2
    #                 sd = np.std(prices)
    #         except:
    #             #If error occurs during loadin website or the website does not exist put None
    #             med = 100000
    #             sd = 0
    #         conds = [
    #             med < 40.00,
    #             med < 80.00,
    #             med < 120.00,
    #             med < 180.00,
    #             med < 250.00,
    #             med >= 250.00
    #         ]
    #         # Add prices to dict
    #         game["price_warehouse"] = med if med != 100000 else None
    #         game["price_sell"] = med + 0.5 * sd if med != 100000 else None
    #         borrow_price = int(np.select(conds, vals))
    #         game["price_borrow"] = borrow_price if borrow_price != 10000 else None
    #         # Update data frames
    #         games.loc[len(games)] = game
    #         # games = games.append(game, ignore_index = True) Depreciated
    #         tags.update(tags_)
    #         iter += 1
    #         if iter >= LIMIT:
    #             break
    #     except Exception as e:
    #         print("Connection error for {}\nError message:{}".format(link, e))

    #         # Czy turniejowa: round((players > 1) * random.random())

    #         # Terminy zwrotów generujemy jako data pobrania + czas między 1-6dni, aby zwrot nastąpił w godzinach pracy skleu

    # driver.close()
    # driver.quit()
    # # Save scraped data to csv file despite the connection status
    # games.to_csv('games.csv', index = False)
    # with open('tags.csv', 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(tags)

    # # Raise exception if connection failed
    # # ---------