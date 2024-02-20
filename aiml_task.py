#!/usr/bin/env python
# coding: utf-8

# In[2]:


import yfinance as yf
import requests
from bs4 import BeautifulSoup
import re

def extract_financial_data(tickers, start_date, end_date):
    financial_data = {}
    for ticker in tickers:
        ticker_data = yf.Ticker(ticker)
        try:
            financials = ticker_data.financials.loc[start_date:end_date]
        except KeyError:
            # Adjust start_date and end_date based on available data
            financials = ticker_data.financials
            if start_date not in financials.index:
                start_date = financials.index[0]
            if end_date not in financials.index:
                end_date = financials.index[-1]
            financials = financials.loc[start_date:end_date]
        financial_data[ticker] = financials
    return financial_data

# Function to extract information about Canoo
def extract_canoo_info():
    url = "https://www.press.canoo.com/press-release/merger-announcement"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    canoo_info = {}

    canoo_info['Industry'] = soup.find_all('p')[0].text.strip()
    canoo_info['Size'] = soup.find_all('p')[1].text.strip()
    canoo_info['Growth Rate'] = soup.find_all('p')[2].text.strip() if len(soup.find_all('p')) >= 3 else ""
    canoo_info['Trends'] = soup.find_all('p')[3].text.strip() if len(soup.find_all('p')) >= 4 else ""
    canoo_info['Key Players'] = soup.find_all('p')[4].text.strip() if len(soup.find_all('p')) >= 5 else ""

    competitor_info = []
    for i in range(5, min(15, len(soup.find_all('p')))):
        competitor = soup.find_all('p')[i].text.strip()
        if i + 5 < min(15, len(soup.find_all('p'))):
            market_size = soup.find_all('p')[i + 5].text.strip()
            competitor_info.append((competitor, market_size))

    canoo_info['Competitors'] = competitor_info

    canoo_info['Market Trends'] = soup.find_all('p')[15].text.strip() if len(soup.find_all('p')) >= 16 else ""

    canoo_financials = soup.find_all('p')[max(16, len(soup.find_all('p'))): min(21, len(soup.find_all('p')))]
    canoo_info['Revenue'] = canoo_financials[0].text.strip() if canoo_financials else ""
    canoo_info['Profit Margins'] = canoo_financials[1].text.strip() if len(canoo_financials) >= 2 else ""
    canoo_info['Return on Investment'] = canoo_financials[2].text.strip() if len(canoo_financials) >= 3 else ""
    canoo_info['Expense Structure'] = canoo_financials[3].text.strip() if len(canoo_financials) >= 4 else ""

    return canoo_info

# Function to extract information about Canoo's competitors
def extract_competitors_info():
    url = "https://www.globaldata.com/company-profile/canoo-inc/competitors/?scalar=true&pid=45659&sid=29"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    competitors_info = []

    competitor_comparison_heading = soup.find('h2', text='Competitor comparison')

    if competitor_comparison_heading:
        competitor_cards = competitor_comparison_heading.find_next('div', class_='cell').find_all('div', class_='card company stretch-s-large')

        for card in competitor_cards:
            competitor_name = card.find('span').text.strip()
            competitor_info_sections = card.find_all('section')
            competitor_info = {'Competitor': competitor_name}
            for section in competitor_info_sections:
                header_element = section.find('header')
                if header_element:
                    header = header_element.text.strip()
                    value_element = section.find('p')
                    value = value_element.text.strip() if value_element else competitor_name
                    competitor_info[header] = value
            competitors_info.append(competitor_info)

    return competitors_info

# Function to extract information about electric vehicle market trends
def extract_ev_trends():
    url = "https://www.sisinternational.com/expertise/industries/electric-vehicle-market-research/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    trend_paragraphs = soup.find_all(["p", "h2"])

    extracted_trends = []

    unwanted_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\bContact\s*(:|\s+)one\s*of\s*our\s*global\s*offices\b',
        r'Email\s*direct\s*:\s*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\s*remove\s*this',
    ]

    unwanted_regex = re.compile('|'.join(unwanted_patterns), flags=re.IGNORECASE)

    for element in trend_paragraphs:
        if element.name == "p":
            text = element.get_text()
            cleaned_text = re.sub(unwanted_regex, '', text)
            extracted_trends.append(cleaned_text.strip())
        elif element.name == "h2":
            element['style'] = 'font-size: 24px;'

    return extracted_trends

# Function to write all information to a text file
def write_to_text(canoo_info, competitors_info, ev_trends, financial_data):
    with open('conno_info.txt', 'w', encoding='utf-8') as textfile:
        textfile.write("Canoo Information:\n")
        for attribute, value in canoo_info.items():
            if isinstance(value, list):
                textfile.write(f"{attribute}:\n")
                for item in value:
                    textfile.write(f"- {item}\n")
            else:
                textfile.write(f"{attribute}: {value}\n")

        textfile.write("\nCompetitors Information:\n")
        for competitor_info in competitors_info:
            for attribute, value in competitor_info.items():
                textfile.write(f"{attribute}: {value}\n")
            textfile.write("\n")

        textfile.write("\nElectric Vehicle Market Trends:\n")
        for trend in ev_trends:
            textfile.write(f"- {trend}\n")

        textfile.write("\nFinancial Data:\n")
        for ticker, data in financial_data.items():
            textfile.write(f"Financial Data for {ticker}:\n")
            textfile.write(f"{data}\n")
            textfile.write("\n")

# Main function
def main():
    # Define tickers, start and end dates
    tickers = ['GOEV', 'TSLA', 'NIO', 'RIVN', 'LCID']
    start_date = '2023-01-01'
    end_date = '2024-1-31'

    # Extract financial data
    financial_data = extract_financial_data(tickers, start_date, end_date)

    # Extract information about Canoo and its competitors
    canoo_info = extract_canoo_info()
    competitors_info = extract_competitors_info()

    # Extract electric vehicle market trends
    ev_trends = extract_ev_trends()

    # Write all information to a text file
    write_to_text(canoo_info, competitors_info, ev_trends, financial_data)

if __name__ == "__main__":
    main()


# In[ ]:




