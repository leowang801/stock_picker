import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import os

def get_sp500_companies():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'id': 'constituents'})
    df = pd.read_html(str(table))[0]
    return df

def pick_random_companies(companies, n=100):
    return np.random.choice(list(companies), n, replace=False)

def fetch_stock_data(tickers, start_date, end_date):
    stock_data = {}
    for ticker in tickers:
        try: 
            data = yf.download(ticker, start=start_date, end=end_date)
            stock_data[ticker] = data
        except (yf.YFPricesMissingError, yf.YFTzMissingError, yf.YFChartError) as e:
            print(f"Failed to fetch data for {ticker}")
    return stock_data

def calculate_percent_gain(stock_data, tickers):
    percent_gains = {}
    for ticker in tickers:
        data = stock_data.get(ticker)
        if not data.empty:
            start_price = data['Open'].iloc[0]
            end_price = data['Close'].iloc[-1]
            percent_gain = (end_price - start_price) / start_price * 100
            percent_gains[ticker] = percent_gain
    return percent_gains

def calculate_portfolio_performance(percent_gains):
    if percent_gains:
        average = np.mean(list(percent_gains.values()))
        return average
    return 0

def load_sp500_historical_performance(csv_file):
    try:
        # Read the CSV file without skipping rows to inspect the content
        # with open(csv_file, 'r') as f:
        #     lines = [f.readline().strip() for _ in range(20)]
        #     for i, line in enumerate(lines):
        #         print(f"Line {i + 1}: {line}")
        
        # Skip the appropriate number of rows based on inspection
        df = pd.read_csv(csv_file, 
                         skiprows=16,
                         skipfooter=1, 
                         parse_dates=['date'], 
                         skipinitialspace=True, 
                         names=['date', 'value'],
                         engine='python',
                         date_format='%Y-%m-%d')
        df.set_index('date', inplace=True)
        return df
    except pd.errors.ParserError as e:
        print(f"Error parsing the CSV file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return pd.DataFrame()

if __name__ == "__main__":
    sp500_companies = get_sp500_companies()

    start_year =2010    
    end_year = 2023
    performances = []
    years = list(range(start_year, end_year + 1))

    sp500_tickers = sp500_companies['Symbol'].tolist()

    num_iterations = 100
    num_companies = 100
    for year in years:
        yearly_performances = []
        sp500_data = fetch_stock_data(sp500_tickers, f"{year}-01-01", f"{year}-12-31")
        sp500_tickers = sp500_data.keys()

        for i in range(num_iterations):
            random_companies = pick_random_companies(sp500_tickers, num_companies)
            tickers = random_companies.tolist()
            percent_gains = calculate_percent_gain(sp500_data, tickers)
            portfolio_performance = calculate_portfolio_performance(percent_gains)
            yearly_performances.append(portfolio_performance)
            # print(f"Portfolio performance for {year}: {portfolio_performance:.2f}%")
        performances.append((np.mean(yearly_performances)))

    # load historical S&P 500 performance
    csv_path = os.path.join('data', 'sp-500-historical-annual-returns.csv')
    sp500_historical_df = load_sp500_historical_performance(csv_path)
    sp500_historical_performance = sp500_historical_df[pd.to_datetime(sp500_historical_df.index).year.isin(years)]['value'].values

    # Calculate the max, min, average, and median performance
    max_performance = np.max(performances)
    min_performance = np.min(performances)
    average_performance = np.mean(performances)
    median_performance = np.median(performances)
    average_difference_from_sp500 = average_performance - np.mean(sp500_historical_performance)
    # print(f"Number of Iterations: {num_iterations}")
    print(f"Max Performance: {max_performance:.2f}%")
    print(f"Min Performance: {min_performance:.2f}%")
    print(f"Average Performance: {average_performance:.2f}%")
    print(f"Median Performance: {median_performance:.2f}%")
    print(f"Average Difference from S&P 500: {average_difference_from_sp500:.2f}%")

    # Plot the portfolio performance over the years and compare it to the S&P 500
    plt.figure(figsize=(10, 5))
    plt.plot(years, performances, marker='o', linestyle='-', color='b')
    plt.plot(years, sp500_historical_performance, marker='o', linestyle='-', color='r')
    plt.legend(['Portfolio', 'S&P 500'])

    plt.axhline(y=average_performance, color='r', linestyle='--', label=f'Average Performance: {average_performance:.2f}%')
    plt.axhline(y=min_performance, color='b', linestyle='--', label=f'Min Performance: {min_performance:.2f}%')
    plt.axhline(y=max_performance, color='g', linestyle='--', label=f'Max Performance: {max_performance:.2f}%')

    plt.title('Portfolio Performance of Randomly Selected S&P 500 Stocks vs. S&P 500')
    plt.xlabel('Year')
    plt.ylabel('Portfolio Percent Gain')
    plt.grid(True)
    plt.show()