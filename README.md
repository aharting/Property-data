Background:

A friend wanted to see the long-time development of property prices (SEK/sq.m) for a confined area in Stockholm, but this was not a filter option in any of the search engines online.

This program collects prices by web scraping price announcements on Booli and outputs a graph with the SEK/sq.m. If you hover over a point, information about street address, date of sale, total living area, number of rooms, total price and SEK/sq.m will be displayed. A 5-degree polynomial fit follows the trend of all data points. One can filter the search by entering a specific area, number of rooms (interval), total living area (interval).

To try it out, just run the program and follow the instructions in the window that appears. The program is suited for searches in the Östermalm area, but one can easily set up one's own filter on Booli's page, then simply paste the URL into the designated field. Please note that it only works for apartments!

Note that this is just a fun project with a very specific personal application - no efforts have been made to further generalise the program, but the potential is certainly there. 

Example search (the program [uses this Booli filter](https://www.booli.se/slutpriser/nedre+ostermalm,mellersta+ostermalm/874673,874671?maxLivingArea=30&minLivingArea=10&objectType=L%25C3%25A4genhet&rooms=1%252C2&minSoldDate=2015-01-01&maxSoldDate=2021-01-09%20&sort=soldDate:) matching the user input)

![alt text](https://github.com/aharting/Property-data/blob/main/Ska%CC%88rmavbild%202021-01-09%20kl.%2020.02.46.png)
![alt text](https://github.com/aharting/Property-data/blob/main/Ska%CC%88rmavbild%202021-01-09%20kl.%2020.02.30.png)

