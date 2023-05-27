from datetime import datetime, timedelta
import json

import yfinance as yf

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


class PortfolioToolsException(Exception):
    pass


def get_tickers():
    portfolio_file = '{0}/data/portfolio.json'.format(settings.BASE_DIR)
    print('Importing data from file: {}'.format(portfolio_file))

    json_stream = open(portfolio_file)
    json_data = json.load(json_stream)
    json_stream.close()
    return json_data


def get_ticker_url(ticker, term='short', resource_type='chart'):
    """
    :param ticker: Stock symbol for the company
    :param term: short, medium, or long term scale
    :param resource_type: chart or quote
    :return: url for the image or web page
    """
    '''
    &ta=1 gives the 9 month timeline AND trendlines. Without it it's 5 months no trends
    &p=d might be period = days? other option is 'w' which is 24 months
    '''
    if term.strip().lower() not in {'short', 'medium', 'long'}:
        raise PortfolioToolsException('Ticker url term duration \'{0}\' invalid'.format(term))

    if resource_type.strip().lower() not in {'quote', 'chart'}:
        raise PortfolioToolsException('Ticker type \'{0}\' invalid'.format(resource_type))

    short_term = 'https://finviz.com/{0}.ashx?t={1}&ty=c&ta=1&p=d&s=l'.format(resource_type, ticker)  # 4-5 mo w/ trends
    medium_term = 'https://finviz.com/{0}.ashx?t={1}'.format(resource_type, ticker)  # 9 months
    long_term = 'https://finviz.com/{0}.ashx?t={1}&ty=c&ta=0&p=w'.format(resource_type, ticker)  # 24 months

    if term.strip().lower() == 'short':
        return short_term
    elif term.strip().lower() == 'medium':
        return medium_term
    else:
        return long_term


def get_ticker_table(table_title, tickers):
    html_contents = '<h2>{}</h2>\n' \
                    '<table style="width:100%" border="1">\n' \
                    '  <tr>\n' \
                    '    <th>Short term</th>\n' \
                    '    <th>Long term</th>\n' \
                    '  </tr>\n'.format(table_title)

    for ticker in tickers:
        info_url = get_ticker_url(ticker, 'medium', 'quote')
        short_image = get_ticker_url(ticker, 'short')
        long_image = get_ticker_url(ticker, 'long')
        html_contents += '<tr><td><a href={0}>{1}</a></td></tr>\n'.format(info_url, info_url)
        html_contents += '' \
                         '  <tr>\n' \
                         '    <td><img src={0}></td>\n' \
                         '    <td><img src={1}></td>\n' \
                         '  </tr><tr></tr>\n'.format(short_image, long_image)
    html_contents += '</table>\n'

    return html_contents


def index(request):
    # Get tickers

    tickers = get_tickers()
    current_tickers = tickers['current_tickers']
    previous_tickers = tickers['previous_tickers']

    # Build html
    html_contents = '<h1>Portfolio viewer</h1>\n'
    html_contents += get_ticker_table("Current tickers", current_tickers)
    html_contents += get_ticker_table("Previous tickers", previous_tickers)

    print('html_contents: {}'.format(html_contents))
    return HttpResponse(html_contents)


def prices(request):
    """
    Playing with caching
    - Getting from redis (running natively, locally) is <1ms
    - Getting from the library is ~250m. Needed to move the timestamps due to lazy loading of data

    TODO -
    - Can we async update the frontend so it doesn't take forever to display results?
    """
    html_contents = '<h1>Current prices</h1>'

    table_header = "Ticker || Price || is cached? || time to retrive data"  #obv not a real table header
    html_contents += table_header + "<br><br>"

    print('getting tickers')
    tickers = get_tickers()

    all_tickers = []
    for tickers_list in tickers.values():
        all_tickers.extend(tickers_list)

    ticker_prices_cached = []
    for ticker in all_tickers:
        print(ticker)
        # Check the cache
        cache_key = "{}_last_price".format(ticker)
        t1 = datetime.now()
        ticker_info_data = cache.get(cache_key)
        t2 = datetime.now()
        time_to_retrive = (t2 - t1).total_seconds()
        if ticker_info_data:
            # TODO - maybe kick off async worker here to update the prices?
            # print('found ticker info in cache:', ticker)
            cache.touch(cache_key)
            price = ticker_info_data.get("currentPrice", None)
            ticker_prices_cached.append((ticker, price, True, time_to_retrive))
        else:
            # print('ticker not in cache, getting and setting')
            t1 = datetime.now()
            ticker_data = yf.Ticker(ticker)
            ticker_info_data = ticker_data.info
            price = ticker_info_data.get("currentPrice", None)
            t2 = datetime.now()
            time_to_retrive = (t2 - t1).total_seconds()
            cache.set(cache_key, ticker_info_data)
            ticker_prices_cached.append((ticker, price, False, time_to_retrive))

        html_content_line = "{}<br>".format(ticker_prices_cached[-1])
        html_contents += html_content_line

    return HttpResponse(html_contents)
