import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

def get_sp500_companies():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'id': 'constituents'})
    df = pd.read_html(str(table))[0]
    return df

def pick_random_companies(companies, n=100, random_state=None):
    return companies.sample(n, random_state=random_state)

def fetch_stock_data(tickers, start_date, end_date):
    stock_data = {}
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        stock_data[ticker] = data
    return stock_data

def calculate_percent_gain(stock_data):
    percent_gains = {}
    for ticker, data in stock_data.items():
        if not data.empty:
            start_price = data['Open'][0]
            end_price = data['Close'][-1]
            percent_gain = (end_price - start_price) / start_price * 100
            percent_gains[ticker] = percent_gain
    return percent_gains

def calculate_portfolio_performance(percent_gains):
    if percent_gains:
        average = np.mean(list(percent_gains.values()))
        return average
    return 0

if __name__ == "__main__":
    sp500_companies = get_sp500_companies()

    start_year = 2023
    end_year = 2023
    performances = []
    years = list(range(start_year, end_year + 1))

    num_iterations = 100
    for i in range(num_iterations):
        random_companies = pick_random_companies(sp500_companies, 100)
        tickers = random_companies['Symbol'].tolist()
        yearly_performances = []
        for year in years:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            stock_data = fetch_stock_data(tickers, start_date, end_date)
            percent_gains = calculate_percent_gain(stock_data)
            portfolio_performance = calculate_portfolio_performance(percent_gains)
            yearly_performances.append(portfolio_performance)
            print(f"Portfolio performance for {year}: {portfolio_performance:.2f}%")
        performances.extend(yearly_performances)

    plt.figure(figsize=(10, 5))
    plt.plot(range(len(performances)), performances, marker='o', linestyle='-', color='b')

    average_performance = np.mean(performances)
    plt.axhline(y=average_performance, color='r', linestyle='--', label=f'Average Performance: {average_performance:.2f}%')

    plt.title('Portfolio Performance of Randomly Selected S&P 500 Stocks in 2023')
    plt.xlabel('Iteration')
    plt.ylabel('Portfolio Percent Gain')
    plt.grid(True)
    plt.show()