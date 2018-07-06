# Stock portfolio tools

### Chart Viewer
The primary objective right now is to have a simple page that displays charts of the tickers in your stock portfolio

#### Deployment
Simply clone the code, then run:
* `pip install -r requirements`
* `python manage.py runserver`

Navigate to `http://<root_url>/portfolio_viewer/` to see a series of charts with links to detailed technicals for each of the stocks in your `data/portfolio.json` file.

#### To-Do list
* Add new column with Dividend
* Dockerize and prepare for kubernetes?
