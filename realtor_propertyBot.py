from urllib import response
from time import sleep
from shutil import which
from scrapy import Selector
import csv
from scrapingbee import ScrapingBeeClient

client = ScrapingBeeClient(api_key='')

# response = client.get()

params =  { 
        'render_js': 'False',
    }

with open('targetCodes.txt', 'r') as f:
    postalCodes = f.readlines()


postalCodes = [x.strip() for x in postalCodes]


with open('Data_New.csv', 'a', newline='', encoding="utf-8-sig") as csvfile:
    fieldnames = [
        "status",
        "address",
        "zip",
        "city",
        "street",
        "year",
        "price",
        "pricePerSqft",
        "beds",
        "baths",
        "area(sqft)",
        "lotSize(sqft)",
        "link",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for postalCode in postalCodes:
        links = [
            "https://www.realtor.com/realestateandhomes-search/" + postalCode + "/",
            # "https://www.realtor.com/realestateandhomes-search/" + postalCode + "/show-recently-sold",
        ]

        for link in links:
            print("Getting: " + link)
            responseMain = client.get(url=link, params=params)
            # print(responseMain.status_code)
            sleep(1)
            
            # with open("page.txt", "w") as f:
            #     f.write(responseMain.content)

            responseMain = Selector(text=responseMain.content)

            while True:
                listings = responseMain.css("a[data-testid='property-anchor']::attr(href)").extract()
                # listings = []
                for listing in listings:
                    print("Scraping:" + listing)

                    response = client.get(url="https://www.realtor.com" + listing, params=params)
                    # sleep(1)
                    # with open("page.txt", "w") as f:
                    #     f.write(responseMain.content)

                    response = Selector(text=response.content)

                    if "sold" in link:
                        status = "Sold"
                    else:
                        status = response.css("span.ldpPage::text").extract()[-1]

                    if "sold" in link:
                        address = response.css("div[data-testid='address-line'] > div::text").extract()
                        address = "".join(address)
                    else:
                        address = response.css("div.address-value > h1::text").extract_first()
                    
                    if address:                        
                        zip = address.split(" ")[-1].strip()
                        city = address.split(",")[1].strip()
                        street = address.split(",")[0].strip()
                    else:
                        zip = ""
                        city = ""
                        street = ""

                    dataPoints = response.css("li.rui-patterns__sc-2lxyoa-0 > div")
                    year = ""
                    pricePerSqft = ""

                    for point in dataPoints:
                        key = point.css("div > span::text").extract_first()
                        value = point.css("div::text").extract_first()
                        if "price" in key.lower():
                            pricePerSqft = value.strip()
                        if "year" in key.lower():
                            year = value.strip()
                    

                    beds = response.css("li[data-testid='property-meta-beds'] > span::text").extract_first()
                    baths = response.css("li[data-testid='property-meta-baths'] > span::text").extract_first()
                    area = response.css("li[data-testid='property-meta-sqft'] > span > span::text").extract_first()
                    lotSize = response.css("li[data-testid='property-meta-lot-size'] > span > span::text").extract_first()

                    if "sold" in link:
                        price = response.css("div[data-testid='last-sold-container'] > h2")
                    else:
                        price = response.css("div.list-price > div::text").extract_first()

                    writer.writerow({
                        "status": status,
                        "address": address,
                        "zip": zip,
                        "city": city,
                        "street": street,
                        "year": year,
                        "price": price,
                        "pricePerSqft": pricePerSqft,
                        "beds": beds,
                        "baths": baths,
                        "area(sqft)": area,
                        "lotSize(sqft)": lotSize,
                        "link": listing
                    })

                    # print({
                    #     "status": status,
                    #     "address": address,
                    #     "zip": zip,
                    #     "city": city,
                    #     "street": street,
                    #     "year": year,
                    #     "price": price,
                    #     "pricePerSqft": pricePerSqft,
                    #     "beds": beds,
                    #     "baths": baths,
                    #     "area(sqft)": area,
                    #     "lotSize(sqft)": lotSize,
                    # })
                
                nextPage = responseMain.css("a[aria-label='Go to next page']::attr(href)").extract_first()
                if nextPage:
                    print("Next Page: " + nextPage)
                    responseMain = client.get(url="https://www.realtor.com" + nextPage, params=params)
                    responseMain = Selector(text=responseMain.content)
                else:
                    print("Next Page: " + "None")
                    break