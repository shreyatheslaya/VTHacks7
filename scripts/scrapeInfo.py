import requests
from bs4 import BeautifulSoup
import threading
import pandas as pd
import random
import csv
# from fake_headers import Headers

class Importer():
    # header = Headers(
    #     # generate any browser & os headeers
    #     headers=False  # don`t generate misc headers
    # )

    # pandas dataframe that we are goin to add all city data to
    dimensions = ['state', 'city', 'cityPopulation', 'populationBySex', 'medianAge', 'zipCodes', 'medianIncome', 'costOfLiving']
    df = pd.DataFrame(columns=dimensions)

    # base url of the website
    homeURL = 'http://www.city-data.com/city/'
    referrer = 'http://www.city-data.com'

    tempProxies = open('proxies.txt').readlines()
    proxies = []

    # list of states to iterate through to get cities
    states = [  "Alabama","Alaska","Arizona","Arkansas","California","Colorado",
                "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
                "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
                "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
                "Nebraska","Nevada","New-Hampshire","New-Jersey","New Mexico","New York",
                "North-Carolina","North-Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
                "Rhode-Island","South Carolina","South-Dakota","Tennessee","Texas","Utah",
                "Vermont","Virginia","Washington","West-Virginia","Wisconsin","Wyoming"]

    citiesPerState = {}

    def __init__(self):
        self.getProxies()
        # for state in self.states[:-2:-1]:
        self.getAllCities(self.states[15:20])
        self.df.to_csv('big.csv')


    def getProxies(self):
        for proxy in self.tempProxies:
            proxy = proxy.strip('\n')
            self.proxies.append({
                            'https://'  :   'https://{}'.format(proxy),
                            'http://'   :   'http://{}'.format(proxy)
            })

        print('Proxies Retrieved\n')

        print(self.proxies)

    # make all requests for a state to get an href to every city in every state
    def getAllCities(self, states):
        threads = [threading.Thread(target=self.getCities, args=(state,)) for state in states]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    # populate the list of cities in each state
    def getCities(self, state):
        print('Getting State:\t{}'.format(state))
        self.citiesPerState[state] = []
        app = '{}.html'.format(state)
        requestURL = self.homeURL + app
        proxy = random.choice(self.proxies)

        try:
            print(requestURL)
            # r = requests.get(requestURL, proxies=prox)
            r = requests.get(requestURL)
            print('MADE REQUEST:\t{}'.format(state))
            r = r.content
            soup = BeautifulSoup(r, features='html.parser')
            tds = soup.find_all('td')
            for td in tds:
                hrefs = td.find_all('a', href=True)
                if hrefs:
                    for href in hrefs:
                        if 'javascript' not in str(href):
                            if '<a href=\"/' not in str(href):
                                self.citiesPerState[state].append(href.get('href'))
        except Exception as e:
            print(e)

        '''
        thread the gathering of individual city information from every
        city in the list of cities for a given state
        '''
        threads = [threading.Thread(target=self.getCityInfo, args=(state, city,)) for city in self.citiesPerState[state]]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        filename = state + '.csv'
        self.df.to_csv(filename)

    # get the city infor given a city name and a state
    def getCityInfo(self, state, city):
        # header = self.header.generate()
        proxy = random.choice(self.proxies)
        try:
            requestURL = self.homeURL + city
            # r = requests.get(requestURL, proxies=proxy)
            r = requests.get(requestURL)
            print(r)
            r = r.content
            soup = BeautifulSoup(r, features='html.parser')
            self.extractCityInformation(state, city, soup)
            print('Got City:\t{}'.format(city))
        except:
            pass

    # function to cleanse the soup of the webpage
    def extractCityInformation(self, state, city, soup):

        responses = {}

        try:
            cityPopulation = soup.find_all('section', {'class':'city-population'})[0].text
        except:
            cityPopulation = 'NaN'

        try:
            populationBySex = soup.find_all('section', {'class':'population-by-sex'})[0].text
        except:
            populationBySex = 'NaN'

        try:
            medianAge = soup.find_all('section', {'class':'median-age'})[0].text
        except:
            medianAge = 'NaN'

        try:
            zipCodes = soup.find_all('section', {'class':'zip-codes'})[0].text
        except:
            zipCodes = 'NaN'

        try:
            medianIncome = soup.find_all('section', {'class':'median-income'})[0].text
        except:
            medianIncome = 'NaN'

        try:
            costOfLiving = soup.find_all('section', {'class':'cost-of-living-index'})[0].text
        except:
            costOfLiving = 'NaN'

        entry = {                   'state'                 : state,
                                    'city'                  : city,
                                    'cityPopulation'        : cityPopulation,
                                    'populationBySex'       : populationBySex,
                                    'medianAge'             : medianAge,
                                    'zipCodes'              : zipCodes,
                                    'medianIncome'          : medianIncome,
                                    'costOfLiving'          : costOfLiving
                                    }

        self.df = self.df.append(entry, ignore_index=True, sort=False)

if __name__ == '__main__':
    i = Importer()
