import datetime as dt
import os
import pandas_datareader.data as web
import pickle
from bs4 import BeautifulSoup as bs
import requests


class Omx30:
    def __init__(self, update=False):
        self.stock_folder = os.path.join(os.getcwd(), 'stock_omx')
        self.companies = self.get_omx30_companies(reload_omx30=update)
        self.stock = self.get_data(reload_stock=update)

    @staticmethod
    def get_omx30_companies(reload_omx30=False):
        company_l = []
        if reload_omx30:
            html_doc = requests.get('https://en.wikipedia.org/wiki/OMX_Stockholm_30').text
            soup = bs(html_doc, 'lxml')
            table = soup.find('table', {'class': 'wikitable sortable'})
            for row in table.findAll('tr')[1:]:
                company_l.append(row.findAll('td')[2].text)

            with open('omx30.pickle','wb') as f:
                pickle.dump(company_l, f)
        else:
            with open('omx30.pickle', 'rb') as f:
                company_l = pickle.load(f)

        return company_l

    def get_data(self, reload_stock=False):
        if reload_stock:
            self.remove_content(self.stock_folder)
            return self.get_data_from_yahoo(self.companies)
        else:
            return self.get_data_from_folder()

    def get_data_from_yahoo(self, company_l):
        stock = {}
        fail_l = []
        today = dt.date.today()
        time_delta = dt.timedelta(weeks=156)
        start = today - time_delta
        end = today

        for company in company_l:
            try:
                df = web.DataReader(company, 'yahoo', start, end)
                df.to_csv('{}/{}.csv'.format(self.stock_folder, company))
                stock[company] = df.reset_index()
            except:
                fail_l.append(company)

        if fail_l:
            stock.update(self.get_data_from_yahoo(fail_l))
        with open('stock.pickle', 'wb') as f:
            pickle.dump(stock, f)

        return stock

    @staticmethod
    def get_data_from_folder():
        with open('stock.pickle', 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def remove_content(path):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))


if __name__ == '__main__':
    a = Omx30(update=False)
    print(a.stock['ABB.ST'].head())
