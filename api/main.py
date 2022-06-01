from bs4 import BeautifulSoup 
from tqdm import tqdm
import pandas as pd # All database operations
import numpy as np  # Numerical operations
import time         # Tracking time
import requests     # HTTP requests
import re           # String manipulation


# Scraping autos
## Configuracion de funciones de busqueda
def getPage(url):
    ''' returns a soup object that contains all the information 
    of a certain webpage'''
    result = requests.get(url)
    if(result.status_code != 200):
        raise Exception(f'Not found{result.status_code}')
    content = result.content
    return BeautifulSoup(content, features = "html")

### Obtencion de primera tab
def tab_info(url):
    
    result = getPage(url)
    card_result = result.findAll('ol',{'class':'ui-search-layout ui-search-layout--grid'})

    #Source Link
    data_href = []
    for car in card_result:
        data_link = car.findAll('a',{'class':'ui-search-result__content ui-search-link'})
        for link in data_link:
            data_href.append(link['href'])

    #Source title card tag
    data_models = []
    for car in card_result:
        data_link = car.findAll('a',{'class':'ui-search-result__content ui-search-link'})
        for link in data_link:
            data_model = link.findAll('h2',{'class':'ui-search-item__title ui-search-item__group__element'})
            for model in data_model:
                data_models.append(model.text)

    #Source price car
    data_prices = []
    for car in card_result:
        data_link = car.findAll('a',{'class':'ui-search-result__content ui-search-link'})
        for link in data_link:
            data_price = link.findAll('span',{'class':'price-tag-fraction'})        
            for price in data_price[0]:
                data_prices.append(price.text)

    #first tab
    df_result = pd.DataFrame({'titulo':data_models,'precio_oferta':data_prices,'Link':data_href})
    
    return df_result

def tab_cars(column_link):

    data_subtitle = []
    data_priceHead = []
    sales = []
    geo_cars = []
    tabs_cars = []
    
    for link in column_link:

        #Consult link from body html
        result = getPage(link)

        try:
            tag_head = result.findAll('div',{'class':'ui-pdp-container__col col-2 ui-vip-core-container--short-description ui-vip-core-container--column__right'})
            tag_head_subtitle = tag_head[0].findAll('span',{'class':'ui-pdp-subtitle'})
            data_subtitle.append(tag_head_subtitle[0].text)
        except:
            data_subtitle.append('Revisar')

        try:
            price_head = result.findAll('span',{'class':'andes-money-amount__fraction'})
            data_priceHead.append(price_head[0].text)
        except:
            data_priceHead.append('Revisar')

        try:
            comp_sales = result.findAll('div',{'class':'ui-vip-profile-info'})
            comp_sales_h3 = comp_sales[0].findAll('h3',{'class':'ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--REGULAR'})
            sales.append(comp_sales_h3[0].text)
        except:
            sales.append('Revisar')

        try:
            geo_car = result.findAll('p',{'class':'ui-seller-info__status-info__subtitle'})
            try:
                geo_cars.append(geo_car[2].text)
            except:
                geo_cars.append(geo_car[1].text)
        except:
            geo_cars.append(geo_car[0].text)
            


        head_car_title = []
        info_tab_car = []
        tab_car = result.findAll('td',{'class':'andes-table__column andes-table__column--left ui-pdp-specs__table__column'})
        title_car = result.findAll('th',{'class':'andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title'})
        for i in tab_car:
            info_tab_car.append(i.text)

        for i in title_car:
            head_car_title.append(i.text)

        db_tab_car = pd.DataFrame([info_tab_car])
        db_tab_car.columns = head_car_title

        tabs_cars.append(db_tab_car)
        


    tab_2 = pd.DataFrame({'subtitulo':data_subtitle,'precio':data_priceHead,'vendedor':sales,'geo_referencia':geo_cars})
    tab_3 = pd.concat(tabs_cars).reset_index(drop=True)
    tab_result = pd.concat([tab_2,tab_3],axis=1)

    return tab_result

def next_pages(url,year,modelo):
    #creation links from iter
    tmp_result = getPage(url)
    try:
        page = tmp_result.findAll('li',{'class':'andes-pagination__page-count'})
        num_page = page[0].text.split(' ')[1] #Number max of next page in web

        db_nextLink = [f'https://autos.mercadolibre.com.mx/{str(modelo)}/desde-{str(year)}/']
    
        i = 48
        for value in range(1,int(num_page)):
                next_link = f'https://autos.mercadolibre.com.mx/{str(modelo)}/desde-{str(year)}/_Desde_{(value*i)+1}_NoIndex_True'
                db_nextLink.append(next_link)
    except:
        db_nextLink = [f'https://autos.mercadolibre.com.mx/{str(modelo)}/desde-{str(year)}/']
    
    return db_nextLink

## Extract full page

# 'chevrolet','volkswagen','nissan',
# 'ford','honda','toyota','mercedes-benz','kia','bmw','acura','alfa-romeo','audi','baic','bentley','marca-buick','cadillac','chrysler','dodge','faw','fiat','gmc','hummer',
# 'hyundai','infiniti','isuzu','jac','jaguar','jeep','lamborghini','land-rover','lincoln','maserati',
# 'mitsubishi','mini','mazda','peugeot','pontiac','porshe','ram','renault','seat','subaru','smart',
# 'suzuki','tesla','toyota',
marcas = ['volvo']


i = 0
for marca in marcas:

    año_inicio = 2012 
    url = f'https://autos.mercadolibre.com.mx/{marca}/desde-{str(año_inicio)}/'
    list_links = next_pages(url,año_inicio,marca)

    dbs_result = []
    for url in tqdm(list_links):
        tab_1 = tab_info(url)
        tab_result = tab_cars(tab_1['Link'])
        df_result = pd.concat([tab_1,tab_result],axis=1)
        date = time.strftime('%d-%m-%Y %H:%M:%S')
        df_result['extraction_day'] = date
        df_result['publicado'] = pd.DataFrame(df_result['subtitulo'].str.split('·').tolist())[1]
        dbs_result.append(df_result)

    df_new = pd.concat(dbs_result).reset_index(drop=True)

    date = time.strftime('%d-%m-%Y')
    df_new.to_csv(f'Data_autos/{marca}_autos_{date}.csv',index=False,encoding='utf-8-sig')
    print(f'--- Done {marca} ---')
    
    i += 1
    if i > 1:
        time.sleep(60)
        i = 0
        print('--------------AWAIT------------------')