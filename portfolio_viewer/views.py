import json

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
    if term.strip().lower() not in {'short', 'medium', 'long'}:
        raise PortfolioToolsException('Ticker url term duration \'{0}\' invalid'.format(term))

    if type.strip().lower() not in {'quote', 'chart'}:
        raise PortfolioToolsException('Ticker type \'{0}\' invalid'.format(type))

    short_term= 'https://finviz.com/{0}.ashx?t={1}&ty=c&ta=0&p=d'.format(type, ticker)  # 4-5 months
    medium_term= 'https://finviz.com/{0}.ashx?t={1}'.format(type, ticker)  # 9 months  # TODO - broken for chart?
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

    # Build html
    html_contents = ''
    for ticker in tickers:
        # Working nicely - all new lines, though
        html_contents += '<p>'
        html_contents += '<img src={0}> '.format(get_ticker_url(ticker, 'short'))
        html_contents += '<img src={0}> '.format(get_ticker_url(ticker, 'long'))

    print('html_contents: {}'.format(html_contents))
    return HttpResponse("Portfolio viewer. Contents:" + html_contents)
