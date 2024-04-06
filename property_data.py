from bs4 import BeautifulSoup
from tkinter import *
import requests
import matplotlib.pyplot as plt
import numpy as np
import datetime
import webbrowser
import re
import seaborn as sns
import pandas as pd

class Gui:
    def __init__(self):
        self.areas={"no":True,"oo":True,"mo":True}
        self.area=[10,30]
        self.rooms=[1,2]
        self.minSoldDate="2023-01-01"
        self.maxSoldDate = str(datetime.datetime.today())[:11]
        self.kde=False
        self.data= {"address":[],"rooms":[],"sqm":[],"price":[],"sqmprice":[],"date":[]}
        self.dct={
            "no": {
                "txt":"nedre+ostermalm",
                "code":"874673",
                "name":"Nedre Östermalm"
            }, "mo": {
                "txt":"mellersta+ostermalm",
                "code":"874671",
                "name":"Mellersta Östermalm"
            }, "oo": {
                "txt":"ovre+ostermalm",
                "code":"874674",
                "name":"Övre Östermalm"
            }
        }

    def url(self,page=None):
        """Gets proper URL for data collection given GUI input data"""
        url = "https://www.booli.se/slutpriser/"
        txts=",".join([self.dct[key]['txt'] for key in self.areas.keys() if key])
        codes=",".join([self.dct[key]['code'] for key in self.areas.keys() if key])
        url += f"{txts}/{codes}/?"
        if self.area[1] is not None:
            url+= f"maxLivingArea={self.area[1]}"
        url += f"&minLivingArea={self.area[0]}&objectType=L%C3%A4genhet"

        if page is not None:
            url+= f"&page={page}"

        url += f"&rooms={self.rooms[0]}"
        rooms="".join([f"%2C{i+1}" for i in range(self.rooms[0], self.rooms[1])])
        url+= f"{rooms}&minSoldDate={self.minSoldDate}&maxSoldDate={self.maxSoldDate}&sort=soldDate"
        return url

    def navigate(self,URL):
        """Creates soup object with HTML code"""
        print(URL)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def nbrItems(self,soup):
        """Retrieves how many items are to be collected in total, across all pages"""
        retrieved = re.findall(r'\b(\d{1,3}(?:\s?\d{3})*)(?=\s|$)\b', soup.find(class_="inline tabular-nums lining-nums mr-1").text)
        try:
            nbr = int(re.sub(r'\s', '', retrieved[0]))
        except:
            print(soup.find(class_="inline tabular-nums lining-nums mr-1").text)
            print(retrieved)
            raise Exception
        return nbr

    def dateOrdinal(self,date):
        """Converts date format to ordinal"""
        d=[int(date.split("-")[i]) for i in range(3)]
        format = datetime.date(d[0], d[1], d[2]).toordinal()
        return format

    def filter(self,soup):
        """Scans the HTML code for sales data, stores in object attributes"""
        property_listings = soup.find_all('article', class_='relative')

        # Iterate through the property listings and extract information
        for listing in property_listings:
            property_name = listing.find('a', class_='expanded-link').text
            date = listing.find('span', class_='text-bui-color-middle-dark').text
            price = listing.find('p', class_='heading-3').text.strip()
            details = [item.text for item in listing.find_all('li', class_='mr-4')]
            try:
                rooms = re.findall(r'(\d+½?) rum', ",".join(details))[0]
            except:
                rooms = "NaN"
            try:
                sqm = re.findall(r'(\d+) m²', ",".join(details))[0]
            except:
                sqm = "NaN"
            try:
                sqmprice = int(int(re.sub(r'\s|kr', '', price))/int(re.findall(r'(\d+) m²', ",".join(details))[0]))
            except:
                sqmprice = "NaN"
            self.data["address"].append(property_name)
            self.data["rooms"].append(rooms)
            self.data["sqm"].append(sqm)
            self.data["sqmprice"].append(sqmprice)
            self.data["price"].append(re.sub(r'kr', '', price))
            self.data["date"].append(self.dateOrdinal(date))
        return


    def getData(self):
        """Given specified input parameters, loops over many pages, calls upon filter to load data from each page"""
        soup = self.navigate(self.url())
        self.filter(soup)
        page = 1
        items = len(self.data["address"])
        nbrApts = self.nbrItems(soup) #number of apartments
        while items < nbrApts:
            page +=1
            nexturl = self.url(page)
            self.filter(self.navigate(nexturl))
            items = len(self.data["address"])
        if len(self.data["address"]) != nbrApts:
            print(f"{nbrApts}, {len(self.data['address'])}")
            raise Exception
        return

    def getDataURL(self,optURL):
        """Given URL, loops over many pages, calls upon filter to load data from each page"""
        soup = self.navigate(optURL)
        self.filter(soup)
        page = 1
        items = 0
        nbrApts = self.nbrItems(soup)
        splitted = optURL.split("genhet")
        while items < nbrApts:
            page += 1
            ext = f"genhet&page={page}"
            nexturl = ext.join(splitted)
            self.filter(self.navigate(nexturl))
            items = len(self.data["address"])
        if len(self.data["address"]) != nbrApts:
            print(f"{nbrApts}, {len(self.data['address'])}")
            raise Exception
        return

    def plot(self,optURL=False):
        """Plots sqm price by date of sale with annotations of additional information of the property sale"""
        if self.kde:
            data=pd.DataFrame(self.data)[['date','sqmprice']]
            sns.relplot(x="date", y="sqmprice", kind="line", data=data)
            plt.show()
            return

        x=self.data["date"]
        y=self.data["sqmprice"]
        fig,ax = plt.subplots()
        canvas = plt.scatter(x, y)

        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.get_bbox_patch().set_alpha(0.4)

        def update_annot(ind):
            pos = canvas.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            index_x=x.index(pos[0])
            while y[index_x] != pos[1]:
                index_x+=1
            text = f"""{self.data['address'][index_x]}
{self.data['price'][index_x]} kr
{self.data['rooms'][index_x]} rum, {self.data['sqm'][index_x]} m² 
{self.data['sqmprice'][index_x]} kr/m²
{datetime.date.fromordinal(x[index_x])}"""

            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor("w")

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = canvas.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        #Reference lines
        #trend = np.polyfit(x, y, 3)
        #trendpoly = np.poly1d(trend)
        #plt.plot(x, trendpoly(x), "r")
        #plt.axhline(y=146000, color='g', linestyle='-') #Referens kvm pris
        plt.axhline(y=105385, color='g', linestyle='-') #Referens kvm pris
        plt.plot()

        #Axis
        first = int(str(datetime.date.fromordinal(min(x))).split("-")[0])
        last = int(str(datetime.date.fromordinal(max(x))).split("-")[0])
        ticks = [datetime.date(y, 1, 1).toordinal() for y in range(first,last+1)]
        plt.xticks(ticks, range(first,last+1))

        if not optURL:
            #Textbox with input data
            textstr = ""
            if self.areas["no"]:
                textstr += "Nedre Östermalm"
                if self.areas["mo"]:
                    textstr += "\nMellersta Östermalm"
                if self.areas["oo"]:
                    textstr += "\nÖvre Östermalm"
            else:
                if self.areas["mo"]:
                    textstr += "Mellersta Östermalm"
                    if self.areas["oo"]:
                        textstr += "\nÖvre Östermalm"
                else:
                    textstr += "Övre Östermalm"

            textstr += "\nkvm: " + str(self.area[0]) + "-" + str(self.area[1]) + "\nrum: " + str(self.rooms[0])+ "-" +str(self.rooms[1])
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,verticalalignment='top', bbox=props)

        plt.show()

    def gui(self):
        """Sets up the GUI with plotting, file dumping and URL collecting functionality"""
        window = Tk()

        window.title("Booli sökstatistik")

        window.geometry('700x300')

        rubric = Label(window, text="Sökning")

        rubric.grid(column=1, row=0)

        area = Label(window, text="Yta")
        area.grid(column=0, row=3)

        rooms = Label(window, text="Antal rum (1-5)")
        rooms.grid(column=0, row=2)

        streck1 = Label(window, text="-")
        streck1.grid(column=2, row=2)

        streck2 = Label(window, text="-")
        streck2.grid(column=2, row=3)

        minAreaEnter = Entry(window, width=5)
        maxAreaEnter = Entry(window, width=5)

        minAreaEnter.grid(column=1, row=3)
        maxAreaEnter.grid(column=3, row=3)


        minAreaEnter.insert(END,str(self.area[0]))
        maxAreaEnter.insert(END,str(self.area[1]))

        minRoomEnter = Entry(window, width=5)
        maxRoomEnter = Entry(window, width=5)

        minRoomEnter.grid(column=1, row=2)
        maxRoomEnter.grid(column=3, row=2)

        minRoomEnter.insert(END,str(self.rooms[0]))
        maxRoomEnter.insert(END,str(self.rooms[1]))

        soldDate = Label(window, text="Försäljningsdatum")
        soldDate.grid(column=0, row=4)

        minSoldDateEnter = Entry(window, width=10)
        maxSoldDateEnter = Entry(window, width=10)

        minSoldDateEnter.grid(column=1, row=4)
        maxSoldDateEnter.grid(column=3, row=4)

        minSoldDateEnter.insert(END, str(self.minSoldDate))
        maxSoldDateEnter.insert(END, str(self.maxSoldDate))

        no_state = BooleanVar()

        no_state.set(self.areas["no"])  # set check state

        noC = Checkbutton(window, text='Nedre östermalm', var=no_state)

        noC.grid(column=0, row=1)

        mo_state = BooleanVar()

        mo_state.set(self.areas["mo"])  # set check state

        moC = Checkbutton(window, text='Mellersta östermalm', var=mo_state)

        moC.grid(column=1, row=1)

        oo_state = BooleanVar()

        oo_state.set(self.areas["oo"])  # set check state

        ooC = Checkbutton(window, text='Övre östermalm', var=oo_state)

        ooC.grid(column=2, row=1)

        def callback(url):
            webbrowser.open_new(url)

        link1 = Label(window, text="Filtrera val via Booli (URL)", fg="blue", cursor="hand2")
        link1.grid(column=0, row=5)
        link1.bind("<Button-1>", lambda e: callback("https://www.booli.se/slutpriser/sverige/77104?objectType=L%C3%A4genhet"))

        optURL = Entry(window,width=20)
        optURL.grid(column=1,row=5)

        def get_input():
            """Collects user input from the GUI"""
            self.areas = {"no": no_state.get(), "oo": oo_state.get(), "mo": mo_state.get()}
            self.area = [int(minAreaEnter.get()), int(maxAreaEnter.get())]
            self.rooms = [int(minRoomEnter.get()), int(maxRoomEnter.get())]
            self.minSoldDate = minSoldDateEnter.get()
            self.maxSoldDate = maxSoldDateEnter.get()
            self.kde = kde_state.get()

        def plotta():
            """Collects the data and creates a sqm price by sales date plot with trendline and annotations incluing additional information about the sale"""
            if optURL.get() == "":
                get_input()
                self.getData()
                self.plot()
            else:
                self.getDataURL(optURL.get())
                self.plot(optURL=True)
            self.__init__()

        def displayUrl():
            """Constructs a URL from the user input and displays it as a link in a new window"""
            get_input()
            url=self.url()

            urlwindow = Tk()
            urlwindow.title("URL")
            urlwindow.geometry('1000x50')

            link1 = Label(urlwindow, text="Länk", fg="blue", cursor="hand2")
            link1.grid(column=0, row=4)
            link1.bind("<Button-1>",lambda e: callback(url))
            self.__init__()
            urlwindow.mainloop()

        def write():
            """Collects data and writes it to a text file"""
            if optURL.get() == "":
                get_input()
                self.getData()
            else:
                self.getDataURL(optURL.get())
            f = open('property_data.txt', 'w')
            for i in range(len(self.data['address'])):
                line = f"{self.data['address'][i]}, {self.data['price'][i]} kr, {self.data['rooms'][i]} rum, {self.data['sqm'][i]} m², {self.data['sqmprice'][i]} kr/m², {datetime.date.fromordinal(self.data['date'][i])} \n"
                f.write(line)
            f.close()
            self.__init__()
            return

        doPlot = Button(window, text="Visa graf", command=plotta, width=10)

        doPlot.grid(column=0, row=6)

        kde_state = BooleanVar()

        kde_state.set(False)  # set check state

        kde = Checkbutton(window, text='KDE', var=kde_state)

        kde.grid(column=1, row=6)

        doUrl = Button(window, text="Hämta url", command=displayUrl, width=10)

        doUrl.grid(column=0, row=7)

        doWrite = Button(window, text="Skriv data till fil", command=write, width=15)

        doWrite.grid(column=0, row=8)

        window.mainloop()

def main():
    app=Gui()
    app.gui()

if __name__ == '__main__':
    main()
    #app=Gui()
    #app.getData()
    # app.kde=True
    # app.plot()
