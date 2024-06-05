import selenium
from selenium.webdriver.common.by import By                             # get elemen with selector       
from selenium import webdriver as wb                                    # run driver
from selenium.webdriver.support import expected_conditions as EC        # EC to wait until
from selenium.webdriver.support.ui import WebDriverWait as wait         # wait suspend action
from bs4 import BeautifulSoup                                           # to use html parser
import pandas as pd                                                     # df
import time                                                             # to sleep
import datetime                                                         # timestamp


def scroll(driver):
    # wait until body loaded
    wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#zeus-root')))
    time.sleep(1)

    scroll_position = 0
    increment = 100
    # get total height to scroll
    total_height = driver.execute_script("return document.body.scrollHeight")
    
    # loop to scroll by increasing position and executing js script
    while True:
        driver.execute_script("window.scrollTo(0, %s);" % scroll_position)
        # sleep to wait content load while scrolling
        time.sleep(0.1)   
        scroll_position += increment
        
        # get updated height if any
        new_total_height = driver.execute_script("return document.body.scrollHeight")
        
        # stop scroll if already at bottom
        if scroll_position >= new_total_height and new_total_height == total_height:
            break
        total_height = new_total_height


def extract_data(category):
    # initializing empty list for product data
    data=[]
    category_name = None

    # searching xiaomi product from official store order by newest for 3 categories
    url_wearable_device = 'https://www.tokopedia.com/search?navsource=&ob=9&sc=3081&shop_tier=2&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=xiaomi'
    url_tablet = 'https://www.tokopedia.com/search?navsource=&ob=9&sc=276&shop_tier=2&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=xiaomi'
    url_handphone = 'https://www.tokopedia.com/search?navsource=&ob=9&sc=24&shop_tier=2&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=xiaomi'

    # switching urls 
    if category == 1:
        url = url_wearable_device
        category_name = "Wearable Device"
    elif category == 2:
        url = url_tablet
        category_name = "Tablet"
    else:
        url = url_handphone
        category_name = "Handphone"
    print("Getting data from category: "+category_name)

    # initializing selenium using edge
    driver = wb.Edge()
    driver.get(url)
    time.sleep(4)

    # looping by how much page is extracted
    for i in range(2):
        scroll(driver)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source,'html.parser')
        
        # looping by all product card
        for item in soup.findAll('div',class_="css-54k5sq"):
            # couldnt get why it sometimes return empty product, so I added break
            product_name = item.find('div',class_="prd_link-product-name css-3um8ox")
            if not product_name:
                break 
            else:
                product_name = product_name.text
            
            # initializing default value for prices
            product_full_price=0
            product_off_price=0
            product_discount=0

            # condition if product have a discount
            if item.find('div',class_="prd_label-product-slash-price css-xfl72w"):
                # cleaning price by removing Rp.
                product_full_price_dirty = item.find('div',class_="prd_label-product-slash-price css-xfl72w").text.replace('Rp','').replace('.','')
                product_off_price_dirty = item.find('div',class_="prd_link-product-price css-h66vau").text.replace('Rp','').replace('.','')
                
                # some products use Juta(jt) and some product have muliple variant so they have multiple prices using - . We clean it here
                if product_full_price_dirty.find('jt')>=0:
                    product_full_price = int(float(product_full_price_dirty.replace(',','.').replace('jt','').partition(' - ')[0])*1000000)
                else:
                    product_full_price = int(product_full_price_dirty)
                if product_off_price_dirty.find('jt')>=0:
                    product_off_price = int(float(product_off_price_dirty.replace(',','.').replace('jt','').partition(' - ')[0])*1000000)
                else:
                    product_off_price = int(product_off_price_dirty)
                product_discount= product_full_price - product_off_price
            else:
                product_full_price_dirty = item.find('div',class_="prd_link-product-price css-h66vau").text.replace('Rp','').replace('.','')
                if product_full_price_dirty.find('jt')>=0:
                    product_full_price = int(float(product_full_price_dirty.replace(',','.').replace('jt','').partition(' - ')[0])*1000000)
                else:
                    product_full_price = int(product_full_price_dirty)

            # getting location and shop name
            shop_loc = item.find('span',class_="prd_link-shop-loc css-1kdc32b flip").text
            shop_name = item.find('span',class_="prd_link-shop-name css-1kdc32b flip").text

            # initializing default value for rating and sold
            avg_rating = 0
            sold = 0
            sold_is_more = 0
            for item_avg_sold in item.findAll('div',class_="prd_shop-rating-average-and-label css-26zmlj"):
                # condition if there is a rating
                if item_avg_sold.find('span',class_='prd_rating-average-text css-t70v7i'):
                    avg_rating = float(item_avg_sold.find('span',class_='prd_rating-average-text css-t70v7i').text)
                # # condition if there is a sold unit
                if item_avg_sold.find('span',class_='prd_label-integrity css-1sgek4h'):
                    sold = item_avg_sold.find('span',class_='prd_label-integrity css-1sgek4h').text
                    # sold apears with + terjual. Cleaning it here and remove. Also added an indicator to see if a product sold contains + or the exact sold value
                    if sold.find('+ ')>=0:
                        sold_is_more = 1
                        sold = sold.replace('+ terjual','')
                    else:
                        sold = sold.replace('terjual','')

            # appending to the list
            data.append((
                product_name,
                product_full_price,
                product_off_price,
                product_discount,
                shop_loc,
                shop_name,
                avg_rating,
                sold,
                sold_is_more,
                category_name
            ))
        
        # click the next page
        wait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Laman berikutnya"]'))).click()
        time.sleep(4)

    # summarize all data appended to the list as a dataframe
    data_df = pd.DataFrame(data, columns=[
        'product_name',
        'product_full_price',
        'product_off_price',
        'product_discount',
        'shop_loc',
        'shop_name',
        'avg_rating',
        'sold',
        'sold_is_more',
        'category_name'
    ])
    driver.close()
    return data_df

# Initializing empty list for all categories
data_list=[]

# looping 3 times to get 3 categories
for i in range(3):
    data_list.append(extract_data(i+1))

# union all data from all category into a single df
data_df = pd.concat(data_list, ignore_index=True)

# creating timestamp
now = datetime.datetime.now()
unix_timestamp = now.timestamp()

# saving df as a csv and json
data_df.to_csv(f'tokopedia_xiaomi_data_{unix_timestamp}.csv')
data_df.to_json(f'tokopedia_xiaomi_data_{unix_timestamp}.json',orient='records')




git remote add origin https://github.com/kalerr/kredivo_group_assesment.git
git branch -M main
git push -u origin main