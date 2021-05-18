from requests import Session, get
from bs4 import BeautifulSoup
from json import dumps, loads
import csv
from tqdm import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from argparse import ArgumentParser

class SSD: 
    def __init__(self, name, password, ano_min, ano_max):
        self.headers = {}
        self.cookies = {}
        self.name = name
        self.password = password
        self.ano_min = ano_min
        self.ano_max = ano_max

        self.get_page()
        
    def get_page(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://app.seg-social.pt/sso/login')
        driver.find_element_by_id('username').send_keys(str(self.name))
        driver.find_element_by_id('password').send_keys(str(self.password))
        driver.find_element_by_name('submitBtn').click()


if __name__ == "__main__":
    
    parser = ArgumentParser(description='Seg-social direta extrato renumerações')
    parser.add_argument('-u','--user', help='Account ID', required=True)
    parser.add_argument('-p','--pw', help='Account password', required=True)
    parser.add_argument('-d','--data', default="1989/2021", help='1989/2021', required=True)

    args = parser.parse_args()

    SSD(args.user, args.pw, args.data.split('/')[0], args.data.split('/')[1]).get_data()