# Spider
This repo comprises a scrapper written in Python, which supports scraping indeed.com for now.

# Features
It takes two files as input. one for the job list and another for locations.
Depth of crawling must be specified else it will set the default depth to 3.
- It is a multi-threaded scrapper. for each querry it initialises a thread.
- Provides inbuilt Proxy pool API, IP rotater.
- Requests are made at random interval for real user simulation.
- Data is stored in pandas dataframe and dumped into a json file.
