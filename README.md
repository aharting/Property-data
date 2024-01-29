### About

We wanted to see the long-time development of property prices **(SEK/sq.m)** for a confined area in Stockholm, but this is not a filter option in any of the search engines online.

This program collects prices by web scraping price announcements on Booli and outputs a graph with the SEK/sq.m. If you hover over a point, information about street address, date of sale, total living area, number of rooms, total price and SEK/sq.m will be displayed. A 5-degree polynomial fit follows the trend of all data points. One can filter the search by entering a specific area, number of rooms (interval), total living area (interval).

To try it out, just run the program and follow the instructions in the window that appears. It can be used in two ways:
* If you would like to look at Östermalm specfifically, enter input values directly into the window
* Else, set up your own filter on Booli's page by doing an "end price search" (Slutpriser). Then, paste the URL into the designated field.

Note that this is just a fun project with a very specific personal application - no efforts have been made to further generalise the program, but the potential is certainly there. 

### Example search with filter through the application:

Input

![Aplication input](https://github.com/aharting/Property-data/blob/main/Example_pictures_GUI_input/Example_input.png)

Ouput (text boxes appear as one hovers over the canvas)

![Application output](https://github.com/aharting/Property-data/blob/main/Example_pictures_GUI_input/Example_output.png)

The program has constructed [this Booli filter](https://www.booli.se/slutpriser/nedre+ostermalm,mellersta+ostermalm/874673,874671?maxLivingArea=30&minLivingArea=10&objectType=L%25C3%25A4genhet&rooms=1%252C2&minSoldDate=2015-01-01&maxSoldDate=2021-01-09%20&sort=soldDate:) matching the user input

### Example search with filter through the Booli website

Construct filter on Booli website

![Construct filter on Booli website](https://github.com/aharting/Property-data/blob/main/Example_pictures_Booli_URL_input/Example_Booli_search.png)

Copy the resulting URL

![Copy the resulting URL](https://github.com/aharting/Property-data/blob/main/Example_pictures_Booli_URL_input/Example_Booli_searchresult.png)

Paste the URL into the application

![Paste the URL into the application](https://github.com/aharting/Property-data/blob/main/Example_pictures_Booli_URL_input/Example_Booli_pasteUrl.png)

Application output

![Application output](https://github.com/aharting/Property-data/blob/main/Example_pictures_Booli_URL_input/Example_Booli_output_hoverpoint2.png)
