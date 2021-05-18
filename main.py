import requests
from bs4 import BeautifulSoup
from json import dumps, loads
import csv
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
from argparse import ArgumentParser
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class SSD: 
    def __init__(self, name, password, ano_min, ano_max):
        self.headers = {}
        self.cookies = {}
        self.name = name
        self.password = password
        self.ano_min = ano_min
        self.ano_max = ano_max
        self.pdData = pd.DataFrame({'Data': [], 'Dias': [], 'Origem': []})

        self.get_page()
        
    def get_page(self):
        
        # Start WebDriver
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.maximize_window()
        
        # Go to info page
        driver.get('https://app.seg-social.pt/sso/login')
        driver.find_element_by_id('username').send_keys(str(self.name))
        driver.find_element_by_id('password').send_keys(str(self.password))
        driver.find_element_by_name('submitBtn').click()

        driver.get('https://app.seg-social.pt/ptss/cci/carreiraContributiva/consultar')
        
        # Wait for necessary element to load 
        Driver_wait = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, "ui-commandlink.ui-widget")))
        ActionChains(driver).move_to_element(Driver_wait).perform()
        
        driver.find_elements_by_class_name("ui-commandlink.ui-widget")[0].click()

        for ano in tqdm(range(int(self.ano_min), int(self.ano_max)+1)):
            
            # Select current year from dropdown menu
            Driver_wait = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "mainForm:ano_label")))
            ActionChains(driver).move_to_element(Driver_wait).perform()

            driver.find_element_by_id('mainForm:ano_label').click()

            Driver_wait = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "mainForm:ano_filter")))
            ActionChains(driver).move_to_element(Driver_wait).perform()

            driver.find_element_by_id('mainForm:ano_filter').send_keys(str(ano))
            driver.find_element_by_id('mainForm:ano_filter').send_keys(Keys.ENTER)

            Driver_wait = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'ui-datatable-tablewrapper')))
            ActionChains(driver).move_to_element(Driver_wait).perform()

            driver.find_elements_by_class_name("ui-commandlink.ui-widget")[0].click()

            for mes in range(0,12):
                
                # Select current month from dropdown menu
                Driver_wait = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="mainForm:mes"]')))
                ActionChains(driver).move_to_element(Driver_wait).perform()

                driver.find_element_by_xpath('//*[@id="mainForm:mes"]').click()

                try:
                    driver.find_element_by_xpath('//*[@id="mainForm:mes_' + str(mes) +'"]').click()
                    
                    Driver_wait = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'ui-datatable-tablewrapper')))
                    ActionChains(driver).move_to_element(Driver_wait).perform()
                    
                    # Get table data using pandas 
                    tempData = pd.read_html(driver.page_source)[0].drop(['Unnamed: 2'], axis=1)  # remove 'Unnamed: 2' collumn
                    tempData['Data'] = "{:02d}/{:4d}".format(mes+1, ano)  # add 'Data' collumn with month/year
                    
                    self.pdData = self.pdData.append(tempData) # append current page data to main dataframe 
                except:
                    # If current month doesn't exist ==> for = break
                    break

        #with open("index.html", "w") as file:
        #    file.write(str(soup))

    def save_data(self, valor):
        if valor:
            self.pdData.drop(['Valor'], axis=1)  # remove 'Valor' collumn according to user option
        self.pdData.to_csv("output.csv", index=False)  # save data to .csv format (excel)
        pass

    
if __name__ == "__main__":
    
    parser = ArgumentParser(description='Seg-social direta extrato renumerações')
    parser.add_argument('-u','--user', help='Account ID', required=True)
    parser.add_argument('-p','--pw', help='Account password', required=True)
    parser.add_argument('-d','--data', default="2000/2021", help='AnoInicio/AnoFim do extrato ex:1989/2021')
    parser.add_argument('--valor', default=True, help='Eliminar coluna valor? (True/False)')

    args = parser.parse_args()

    SSD(args.user, args.pw, args.data.split('/')[0], args.data.split('/')[1]).save_data(args.valor)
