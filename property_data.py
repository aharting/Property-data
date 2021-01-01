from bs4 import BeautifulSoup
from tkinter import *
import requests
import matplotlib.pyplot as plt
import numpy as np
import datetime
import webbrowser

class Gui:
    def __init__(self):
        self.areas={"no":True,"oo":True,"mo":True}
        self.area=[10,30]
        self.rooms=[1,2]
        self.minSoldDate="2015-01-01"
        self.maxSoldDate = str(datetime.datetime.today())[:11]
        self.data= {"address":[],"rooms":[],"sqm":[],"price":[],"priceSqm":[],"date":[]}

    def restart(self):
        """Clears the attributes"""
        self.areas={"no":True,"oo":False,"mo":False}
        self.area=[10,30]
        self.rooms=[0,2]
        self.minSoldDate="2015-01-01"
        self.maxSoldDate = str(datetime.datetime.today())[:11]
        self.data= {"address":[],"rooms":[],"sqm":[],"price":[],"priceSqm":[],"date":[]}

    def url(self,page=None):
        """Gets proper URL for data collection given GUI input data"""
        areaText =[]
        areaCode = []

        url = "https://www.booli.se/slutpriser/"
        if self.areas["no"] == True:
            areaText.append("nedre+ostermalm")
            areaCode.append("874673")
        if self.areas["mo"] == True:
            areaText.append("mellersta+ostermalm")
            areaCode.append("874671")
        if self.areas["oo"] == True:
            areaText.append("ovre+ostermalm")
            areaCode.append("874674")
        areaText=",".join(areaText)
        areaCode=",".join(areaCode)
        url += areaText + "/" + areaCode + "/?"
        if self.area[1] is not None:
            url+= "maxLivingArea=" + str(self.area[1])
        url += "&minLivingArea=" + str(self.area[0]) + "&objectType=L%C3%A4genhet"

        if page is not None:
            url+= "&page=" + str(page)

        url += "&rooms=" + str(self.rooms[0])
        rooms = ""
        for i in range(self.rooms[0]+1, self.rooms[1]+1):
            rooms += "%2C"+str(i)
        url+= rooms + "&" + "minSoldDate=" + self.minSoldDate  + "&maxSoldDate=" + self.maxSoldDate
        url+="&sort=soldDate"
        return url

    def navigate(self,URL):
        """Creates soup object with HTML code"""
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def nbrItems(self,soup):
        """Retrieves how many items are to be collected in total, across all pages"""
        nbr = int(soup.find(class_="EuKIv _36W0F").text.split(" ")[-1])
        return nbr

    def dateOrdinal(self,date):
        """Converts date format to ordinal"""
        d=[int(date.split("-")[i]) for i in range(3)]
        format = datetime.date(d[0], d[1], d[2]).toordinal()
        return format

    def filter(self,soup):
        """Scans the HTML code for sales data, stores in object attributes"""
        aptClass = "pnQPJ"
        addressClass = 'w9WmR mPmHV'
        areaClass = "_3f7tk _36W0F MJN7s _2wUYk"
        priceClass = '_3jVNK _36W0F _2q4-- _4ym7M'

        apts = soup.find_all(class_=aptClass)
        for apt in apts:
            self.data["address"].append(apt.find(class_= addressClass).text)
            self.data["rooms"].append(apt.find(class_=areaClass).find('p').text.split(", ")[0])
            self.data["sqm"].append(apt.find(class_=areaClass).find('p').text.split(", ")[1])
            self.data["price"].append(apt.find(class_=priceClass).find('h4').text)
            self.data["priceSqm"].append(int("".join(apt.find(class_=priceClass).find_all('p')[0].text.split(" kr/")[0].split(" "))))
            self.data["date"].append(self.dateOrdinal(apt.find(class_=priceClass).find_all('p')[1].text))
        return


    def getData(self):
        """Given specified input parameters, loops over many pages, calls upon filter to load data from each page"""
        soup = self.navigate(self.url())
        self.filter(soup)
        page = 1
        items = 0
        nbrApts = self.nbrItems(soup) #number of apartments
        while items < nbrApts:
            page +=1
            nexturl = self.url(page)
            self.filter(self.navigate(nexturl))
            items = len(self.data["address"])
        assert len(self.data["address"]) == nbrApts
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
            ext = "genhet" + "&page=" + str(page)
            nexturl = ext.join(splitted)
            self.filter(self.navigate(nexturl))
            items = len(self.data["address"])
        assert len(self.data["address"]) == nbrApts
        return

    def plot(self,optURL=False):
        """Plots sqm price by date of sale with annotations of additional information of the property sale"""
        y=self.data["priceSqm"]
        x=self.data["date"]

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
            text = self.data["address"][index_x]+ "\n" + self.data["price"][index_x]+"\n" + self.data["rooms"][index_x] + ", " + self.data["sqm"][index_x] + "\n" + str(self.data["priceSqm"][index_x]) + " kr/m²" + "\n" + str(datetime.date.fromordinal(x[index_x]))
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
        trend = np.polyfit(x, y, 5)
        trendpoly = np.poly1d(trend)
        plt.plot(x, trendpoly(x), "r")
        #plt.axhline(y=105385, color='g', linestyle='-') #Referens kvm pris
        plt.plot()

        #Axis
        first = int(str(datetime.date.fromordinal(min(x))).split("-")[0])
        ticks = [datetime.date(y, 1, 1).toordinal() for y in range(first,2022)]
        plt.xticks(ticks, range(first,2022))

        if optURL == False:
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

        def plotta():
            """Collects the data and creates a sqm price by sales date plot with trendline and annotations incluing additional information about the sale"""
            if optURL.get() == "":
                get_input()
                self.getData()
                self.plot()
            else:
                self.getDataURL(optURL.get())
                self.plot(optURL=True)
            self.restart()

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
            self.restart()
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
                line = self.data['address'][i] + ", " + self.data['price'][i] + ", " + self.data['rooms'][i] + ", " + self.data['sqm'][i] + ", " + str(self.data['priceSqm'][i]) + " kr/m², " + str(datetime.date.fromordinal(self.data['date'][i]))+'\n'
                f.write(line)
            f.close()
            self.restart()
            return

        doPlot = Button(window, text="Visa graf", command=plotta, width=10)

        doPlot.grid(column=0, row=6)

        doUrl = Button(window, text="Hämta url", command=displayUrl, width=10)

        doUrl.grid(column=0, row=7)

        doWrite = Button(window, text="Skriv data till fil", command=write, width=15)

        doWrite.grid(column=0, row=8)

        window.mainloop()

def main():
    app=Gui()
    app.gui()

if __name__ == '__main__': main()

