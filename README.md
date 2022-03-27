# Web_Scraping_YhFinance

Solving the problem was just a matter of gaining acess to the request data. Since the link https://finance.yahoo.com/quote/Ticker/financials?p=Ticker wasn't returning any values I had to gather the data from individual links and then rearrange the data into the desired format.

I used Selenium because it's the most commom library for web scraping, and pandas because it was required. With a large enough database, spark would also be very efficient in cleaning/transformimg the data.

I gatherd all the data from the links so if different fields were required in the future there wouldn't be any need to mess with html code, I would just have to filter the data, just as I did in the code.

In future versions it would be nice to add some code to prevent connectivity issues, user inputing Tickers that dont exist and providing the user the ability to choose which web driver to be utilized.
