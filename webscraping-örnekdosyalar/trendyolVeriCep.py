import requests
import json
from bs4 import BeautifulSoup
class ScrapingTrendyol:
    def __init__(self)->None:
        self.url = 'https://www.trendyol.com/'    
    def get_html_source(self,param=1):
        payload={'pi':param}
        response=requests.get(self.url+"/cep-telefonu-x-c103498",params=payload)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            return soup
        else:
            return response.status_code    
    def get_all_products(self, start_page=1, end_page=12):
        all_products = []
        for page_number in range(start_page, end_page + 1):
            soup = self.get_html_source(page_number)
            products = soup.find('div', attrs={'class':'prdct-cntnr-wrppr'}).find_all('div', attrs={'class':'p-card-wrppr with-campaign-view'})
            all_products.extend(products)
        return all_products
    
    def get_products(self):
        all_products = self.get_all_products()
        print(len(all_products))
        return all_products

    def get_product_name(self):
        products = self.get_products()
        product_names = list(map(lambda product_name: product_name.find('div', 
                        {'class': 'product-down'}).find_all('span')[0].text, products))
        return product_names
    def get_product_link(self):
        products = self.get_products()
        product_links = list(map(lambda product_link: self.url
        + "{}".format(product_link.find('a').get('href')), products))
        for link in product_links:
            print(link)
        return product_links
    def get_product_info(self):
        products = self.get_products()
        product_infos = list(map(lambda product_name: product_name.find('div', 
                            {'class': 'product-down'}).find_all('span')[1].text, products))
        return product_infos    
    def get_product_price(self):
        products = self.get_products()       
        product_prices = list(map(lambda product_price: product_price.find('div',
                {'class': 'prc-box-dscntd'}).text, products))
        return product_prices   


    def merge_product(self):
        product_names = self.get_product_name()
        product_links=self.get_product_link()
        product_infos=self.get_product_info()
        product_prices=self.get_product_price()
        product_list = [{"productName":product_name,
                        "productLink":product_link,"productPrice":product_price,
                        "productInfo":product_info} 
                        for product_name,product_link,product_price,product_info 
                        in zip(product_names, product_links,product_prices, product_infos)]
        return product_list

    def save_json(self, data):
        with open('products02.json','w', encoding="utf-8") as f:
            f.write(json.dumps(data, indent=3, ensure_ascii=False))
            print("kaydedildi")
    
scraping_trendyol=ScrapingTrendyol()
data = scraping_trendyol.merge_product()
print(scraping_trendyol.save_json(data))