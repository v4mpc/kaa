import requests
import bs4
import re
# import logging

# log=logging.basicConfig(filename='kaa.log',format='%(asctime)s %(message)s',level=logging.DEBUG).addHandler(logging.StreamHandler(sys.stdout))
headers={
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

origin_country={
    'AUDI':'GERMANY',
    'BENTLY':'EUROPE',
    'BMW':'GERMANY',
    'CADILLAC':'USA',
    'CHEVROLET':'USA',
    'CHRYSLER':'USA',
    'CITROEN':'FRANCE',
    'DACIA':'EUROPE',
    'DAF':'EUROPE',
    'DAIHATSU':'EUROPE',
    'ERF':'EUROPE',
    'FIAT':'EUROPE',
    'FODEN':'EUROPE',
    'FORD':'EUROPE',
    'FOTON':'CHINA', #EUROPE USA
    'FREIGHTLINER':'CHINA', #EUROPE USA
    'GMC':'USA',
    'HINO':'JAPAN',
    'HONDA':'JAPAN',
    'HOWO':'CHINA',
    'HUMMER':'USA',
    'HYUNDAI':'KOREA',
    'INFINITY':'JAPAN',
    'ISUZU':'JAPAN',
    'IVECO':'EUROPE',
    'JAGUAR':'UNITED KINGDOM',
    'JEEP':'USA',
    'KIA':'KOREA',
    'LANDROVER':'EUROPE',
    'LDV':'EUROPE',
    'LEXUS':'JAPAN',
    'LINCOLIN':'USA',
    'MAN':'EUROPE',
    'MAZDA':'JAPAN',
    'MERCEDES':'EUROPE',
    'MITSUBISHI':'JAPAN',
    'NISSAN':'JAPAN',
    'OPEL':'EUROPE',
    'PEUGEOT':'EUROPE',
    'PORSCHE':'GERMANY',
    'RENALT':'EUROPE',
    'SAAB':'EUROPE',
    'SCANIA':'EUROPE',
    'SMART':'EUROPE',
    'SSANGYONG':'KOREA',
    'SUBARU':'JAPAN',
    'SUZUKI':'JAPAN',
    'TOYOTA':'JAPAN',
    'VAUXHALL':'EUROPE',
    'VOLKSWAGEN':'GERMANY',
    'VOLVO':'EUROPE'
}

def get_car_props(url):
    # logging.info("Connecting to Beforward.com")
    resp=requests.get(url,headers=headers).text
    soup=make_soup(resp)
    car=extract_all_specs(soup)
    return {
    'make':extract_make(url),
    'model':extract_model(car),
    'year':extract_year(car),
    'country':extract_country(url),
    'fuel':extract_fuel(car),
    'engine':extract_engine(car),
    'price':extract_price(car),
    'body':extract_body(car),
    'image':extract_image(car),
    'chassis':extract_chassis(car)
    }
    
def extract_image(car):
    return car['image']

def extract_body(car):
    return car['body']

def extract_model(car):
    return car['model']

def extract_price(car):
    return re.sub(r'\(TSh|\)|,| ','',car['price'])
    

def extract_make(url):
    result=re.search(r'beforward\.jp\/([a-z-]+)+',url)
    return result.group(1).split('-')[0]


def extract_year(car):
    year=car['manufactureyearmonth']
    # print(year)
    if year == '-' or year =='N/A':
        return car['registrationyearmonth'].split('/')[0]
    return car['manufactureyearmonth'].split('/')[0]

def extract_engine(car):
    return re.sub(r',|c','',car['enginesize'])

def extract_chassis(car):
    return car['chassis'];

def extract_fuel(car):
    return car['fuel']

def extract_country(url):
    make=extract_make(url).upper()
    # print(make)
    return origin_country[make]
    
    

def make_key(name):
    name=name.lower()
    return re.sub(r'\s|#|\/|\.|','',name)

def clean(text):
    return re.sub(r'/\n|/\t|\s|','',text)

def extract_all_specs(soup):
    spec_div=soup.find_all(id='spec')[0]
    all_tr=spec_div.find_all('tr')
    td_values=[]
    car_props={}
    for tr in all_tr:
       tr_contents=list(filter(lambda x:x!="\n",tr))
       if len(tr_contents) == 4:
            car_props[make_key(tr_contents[0].text)]=clean(tr_contents[1].text)
            car_props[make_key(tr_contents[2].text)]=clean(tr_contents[3].text)

    spec_ul=soup.find_all(id='bread')[0]
    all_li=spec_ul.find_all('li')
    car_props['model']=all_li[3].a.text
    car_props['body']=all_li[2].a.text
    car_props['image']=soup.find_all(id='mainImage')[0]['src']
    car_props['price']=soup.find_all(class_='ip-sh-price')[0].text
    # print(car_props['image'])
    # print(car_props)
    return car_props



def make_soup(resp):
    return bs4.BeautifulSoup(resp,'lxml')



# soup=make_soup(resp.text)
# print(get_car_props(url))