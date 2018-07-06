import json

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


class PortfolioToolsException(Exception):
    pass

def get_tickers():
    portfolio_file = '{0}/data/portfolio.json'.format(settings.BASE_DIR)
    print('Importing data from file: {}'.format(portfolio_file))

    json_stream = open(portfolio_file).read()
    json_data = json.loads(json_stream)
    return json_data['data']


def get_ticker_url(ticker, term='short', type='chart'):
    """
    :param ticker: Stock symbol for the company
    :param term: short, medium, or long term scale
    :param type: chart or quote
    :return: url for the image or web page
    """
    '''
    &ta=1 gives the 9 month timeline AND trendlines. Without it it's 5 months no trends
    &p=d might be period = days? other option is 'w' which is 24 months
    '''
    if term.strip().lower() not in {'short', 'medium', 'long'}:
        raise PortfolioToolsException('Ticker url term duration \'{0}\' invalid'.format(term))

    if type.strip().lower() not in {'quote', 'chart'}:
        raise PortfolioToolsException('Ticker type \'{0}\' invalid'.format(type))

    short_term = 'https://finviz.com/{0}.ashx?t={1}&ty=c&ta=1&p=d&s=l'.format(type, ticker)  # 4-5 mo w/ trends
    medium_term = 'https://finviz.com/{0}.ashx?t={1}'.format(type, ticker)  # 9 months
    long_term = 'https://finviz.com/{0}.ashx?t={1}&ty=c&ta=0&p=w'.format(type, ticker)  # 24 months

    if term.strip().lower() == 'short':
        return short_term
    elif term.strip().lower() == 'medium':
        return medium_term
    else:
        return long_term


def index(request):
    # Get tickers
    tickers = get_tickers()

    import pytz

    # Build html
    html_contents = '<h2>Portfolio viewer</h2>' \
        'Time: {0}' \
        '<table style="width:100%" border="1">' \
        '  <tr>' \
        '    <th>Short term</th>' \
        '    <th>Long term</th>' \
        '  </tr>'.format(str(datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M %p")))

    for ticker in tickers:
        info_url = get_ticker_url(ticker, 'medium', 'quote')
        short_image = get_ticker_url(ticker, 'short')
        long_image = get_ticker_url(ticker, 'long')
        html_contents += '<tr><td><a href={0}>{1}</a></td></tr>'.format(info_url, info_url)
        html_contents += '' \
        '  <tr>' \
        '    <td><img src={0}></td>' \
        '    <td><img src={1}></td>' \
        '  </tr><tr></tr>'.format(short_image, long_image)

    print('html_contents: {}'.format(html_contents))
    return HttpResponse(html_contents)
