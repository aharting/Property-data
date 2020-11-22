from bs4 import BeautifulSoup
from tkinter import *
import requests
import re
import matplotlib.pyplot as plt
import numpy as np
import datetime

def url(no=False, mo=False, oo=False, minArea=0, maxArea=None, minRooms=1, maxRooms=5,page=None):
    areaText =[]
    areaCode = []

    url = "https://www.booli.se/slutpriser/"
    if no == True:
        areaText.append("nedre+ostermalm")
        areaCode.append("874673")
    if mo == True:
        areaText.append("mellersta+ostermalm")
        areaCode.append("874671")
    if oo == True:
        areaText.append("ovre+ostermalm")
        areaCode.append("874674")
    areaText=",".join(areaText)
    areaCode=",".join(areaCode)
    url += areaText + "/" + areaCode + "/?"
    if maxArea is not None:
        url+= "maxLivingArea=" + str(maxArea)
    url += "&minLivingArea=" + str(minArea) + "&objectType=L%C3%A4genhet"

    if page is not None:
        url+= "&page=" + str(page)

    url += "&rooms=" + str(minRooms)
    rooms = ""
    for i in range(minRooms+1, maxRooms + 1):
        rooms += "%2C"+str(i)
    url+= rooms + "&sort=soldDate"
    return url

def navigate(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def howMany(soup):
    nbr = int(soup.find('h1', class_='search-summary__text').text.split(' ')[0])
    return nbr

def filterToFile(soup):
    out = ""
    apts = soup.find_all('li', class_="search-list__item")
    for apt in apts:
        info1 = apt.find('span',class_="search-list__column search-list__column--info-1")
        info = info1.find_all('span')
        for k in info:
            out+= k.text + ","
        info2 = apt.find('span',class_="search-list__column search-list__column--info-2")
        info = info2.find_all('span')
        for k in info:
            out+= k.text + ","
        out = out[:len(out)-1]
        out += "\n"
    return out

def filterToPlot(soup, data):
    apts = soup.find_all('li', class_="search-list__item")
    for apt in apts:
        row = []
        info1 = apt.find('span',class_="search-list__column search-list__column--info-1")
        info = info1.find_all('span')
        for k in info:
            if re.search("Lägenhet",k.text) == None:
                row.append(k.text)

        info2 = apt.find('span',class_="search-list__column search-list__column--info-2")
        info = info2.find_all('span')
        for k in info:
            if re.search("Lägenhet", k.text) == None:
                row.append(k.text)
        data.append(row)

    return data

def dateConv(date):
    monthDict = {"jan":"01","feb":"02","mar":"03","apr":"04","maj":"05","jun":"06","jul":"07","aug":"08","sep":"09","okt":"10","nov":"11","dec":"12"}

    if len(date[1]) == 1:
        datestr = "0" + date[0] + "/" + monthDict[date[1]] + "/" + date[2]
    else:
        datestr = date[0] + "/" + monthDict[date[1]] + "/" + date[2]
    format = datetime.datetime.strptime(datestr, "%d/%m/%Y").date()
    return format


def plot(data,no,mo,oo,minArea,maxArea,minRooms,maxRooms):
    y = []
    x = []
    d = {}

    for row in data:
        date = dateConv(row[4].split(" ")).toordinal()
        try:
            sqM = int(row[3].replace(" ","")[:-5])
        except:
            sqM = int(row[3].replace(" ", "")[:-6])

        y.append(sqM)
        x.append(date)
        d[(date,sqM)] = row

    fig,ax = plt.subplots()
    sc = plt.scatter(x, y)

    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    annot.get_bbox_patch().set_alpha(0.4)
    annot.set_visible(True)

    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = d[(pos[0],pos[1])]
        s = "\n".join(text)
        annot.set_text(s)
        annot.get_bbox_patch().set_facecolor("w")

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    #Lines
    trend = np.polyfit(x, y, 5)
    trendpoly = np.poly1d(trend)
    plt.plot(x, trendpoly(x), "r")
    #plt.axhline(y=105385, color='g', linestyle='-') #Mitt kvm m pris
    plt.plot()

    #x-axis labels
    early = int(data[len(data)-1][4].split(" ")[2])
    dates = []
    years = range(early,2021,1)
    for y in years:
        datestr = "01/01/" + str(y)
        dates.append(datetime.datetime.strptime(datestr, "%d/%m/%Y").date().toordinal())

    ax.get_xaxis().set_ticks(dates)
    ax.set_xticklabels(years)

    #Textbox with indata
    textstr = ""
    if no:
        textstr += "Nedre Östermalm"
        if mo:
            textstr += "\nMellersta Östermalm"
        if oo:
            textstr += "\nÖvre Östermalm"
    else:
        if mo:
            textstr += "Mellersta Östermalm"
            if oo:
                textstr += "\nÖvre Östermalm"
        else:
            textstr += "Övre Östermalm"

    textstr += "\nkvm: " + str(minArea) + "-" + str(maxArea) + "\nrum: " + str(minRooms)+ "-" +str(maxRooms)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.show()

def plotUrl(data):
    y = []
    x = []
    d = {}

    for row in data:
        date = dateConv(row[4].split(" ")).toordinal()
        try:
            sqM = int(row[3].replace(" ", "")[:-5])
        except:
            sqM = int(row[3].replace(" ", "")[:-6])

        y.append(sqM)
        x.append(date)
        d[(date, sqM)] = row

    fig, ax = plt.subplots()
    sc = plt.scatter(x, y)

    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    annot.get_bbox_patch().set_alpha(0.4)
    annot.set_visible(True)

    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = d[(pos[0], pos[1])]
        s = "\n".join(text)
        annot.set_text(s)
        annot.get_bbox_patch().set_facecolor("w")

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    # Lines
    trend = np.polyfit(x, y, 5)
    trendpoly = np.poly1d(trend)
    plt.plot(x, trendpoly(x), "r")
    #plt.axhline(y=105385, color='g', linestyle='-')  # Mitt kvm m pris
    plt.plot()

    # x-axis labels
    early = int(data[len(data) - 1][4].split(" ")[2])
    dates = []
    years = range(early, 2021, 1)
    for y in years:
        datestr = "01/01/" + str(y)
        dates.append(datetime.datetime.strptime(datestr, "%d/%m/%Y").date().toordinal())

    ax.get_xaxis().set_ticks(dates)
    ax.set_xticklabels(years)
    plt.show()

def write(out, name):
    f = open(name, 'w')
    f.write(out)
    return

def writeToFile(no,mo,oo,minArea,maxArea,minRooms,maxRooms):
    out = ""
    mainurl = url(no,mo,oo,minArea,maxArea,minRooms,maxRooms)
    out+=filterToFile(navigate(mainurl))
    for page in range(2,10):
        nexturl = url(no,mo,oo,minArea,maxArea,minRooms,maxRooms,page)
        out += filterToFile(navigate(nexturl))
    write(out, 'property_data')

def getData(no,mo,oo,minArea,maxArea,minRooms,maxRooms):
    mainurl = url(no,mo,oo,minArea,maxArea,minRooms,maxRooms)
    data = []
    soup = navigate(mainurl)
    filterToPlot(soup, data)
    page = 1
    items = 0
    nbr = howMany(soup)
    while items < nbr:
        page +=1
        nexturl = url(no,mo,oo,minArea,maxArea,minRooms,maxRooms,page)
        filterToPlot(navigate(nexturl), data)
        items = len(data)
    return data

def getDataURL(optURL):
    mainurl = optURL
    data = []
    soup = navigate(mainurl)
    filterToPlot(soup, data)
    page = 1
    items = 0
    nbr = howMany(soup)
    splitted = mainurl.split("genhet")
    while items < nbr:
        page += 1
        ext = "genhet" +"&page=" + str(page)
        nexturl = ext.join(splitted)
        filterToPlot(navigate(nexturl), data)
        items = len(data)
    return data

def gui():

    window = Tk()

    window.title("Booli sökstatistik")

    window.geometry('550x200')

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


    minAreaEnter.insert(END,"0")
    maxAreaEnter.insert(END,"300")

    minRoomEnter = Entry(window, width=5)
    maxRoomEnter = Entry(window, width=5)

    minRoomEnter.grid(column=1, row=2)
    maxRoomEnter.grid(column=3, row=2)

    minRoomEnter.insert(END,"1")
    maxRoomEnter.insert(END,"5")

    no_state = BooleanVar()

    no_state.set(True)  # set check state

    noC = Checkbutton(window, text='Nedre östermalm', var=no_state)

    noC.grid(column=0, row=1)

    mo_state = BooleanVar()

    mo_state.set(True)  # set check state

    moC = Checkbutton(window, text='Mellersta östermalm', var=mo_state)

    moC.grid(column=1, row=1)

    oo_state = BooleanVar()

    oo_state.set(True)  # set check state

    ooC = Checkbutton(window, text='Övre östermalm', var=oo_state)

    ooC.grid(column=2, row=1)

    urlLabel = Label(window, text="Alternativt: URL")
    urlLabel.grid(column=0, row=4)

    optURL = Entry(window,width=20)
    optURL.grid(column=1,row=4)


    def toPlot():

        no = no_state.get()  # Nedre östermalm
        mo = mo_state.get()  # Mellersta östermalm
        oo = oo_state.get()  # Övre östermalm (kan välja flera samtidigt)
        minArea = int(minAreaEnter.get())  # Min kvm
        maxArea = int(maxAreaEnter.get())  # Max kvm, obegränsat = None
        minRooms = int(minRoomEnter.get())  # Min rum tillåtet: (1-5)
        maxRooms = int(maxRoomEnter.get())  # Max rum tillåtet: (1-5)

        if optURL.get() is "":
            plot(getData(no, mo, oo, minArea, maxArea, minRooms, maxRooms), no, mo, oo, minArea, maxArea, minRooms,maxRooms)
        else:
            plotUrl(getDataURL(optURL.get()))

    def dispUrl():
        no = no_state.get()  # Nedre östermalm
        mo = mo_state.get()  # Mellersta östermalm
        oo = oo_state.get()  # Övre östermalm (kan välja flera samtidigt)
        minArea = int(minAreaEnter.get())  # Min kvm
        maxArea = int(maxAreaEnter.get())  # Max kvm, obegränsat = None
        minRooms = int(minRoomEnter.get())  # Min rum tillåtet: (1-5)
        maxRooms = int(maxRoomEnter.get())  # Max rum tillåtet: (1-5)

        urlwindow = Tk()
        urlwindow.title("URL")
        urlwindow.geometry('1000x50')
        URL = Label(urlwindow, text=url(no, mo, oo, minArea, maxArea, minRooms, maxRooms))
        URL.grid(column=0, row=0)
        urlwindow.mainloop()

    def toWrite():
        no = no_state.get()  # Nedre östermalm
        mo = mo_state.get()  # Mellersta östermalm
        oo = oo_state.get()  # Övre östermalm (kan välja flera samtidigt)
        minArea = int(minAreaEnter.get())  # Min kvm
        maxArea = int(maxAreaEnter.get())  # Max kvm, obegränsat = None
        minRooms = int(minRoomEnter.get())  # Min rum tillåtet: (1-5)
        maxRooms = int(maxRoomEnter.get())  # Max rum tillåtet: (1-5)
        writeToFile(no,mo,oo,minArea,maxArea,minRooms,maxRooms)

    doPlot = Button(window, text="Visa graf", command=toPlot, width=10)

    doPlot.grid(column=0, row=5)

    doUrl = Button(window, text="Hämta url", command=dispUrl, width=10)

    doUrl.grid(column=0, row=6)

    doWrite = Button(window, text="Skriv data till fil", command=toWrite, width=15)

    doWrite.grid(column=0, row=7)

    window.mainloop()

def main():
    gui()


if __name__ == '__main__': main()
