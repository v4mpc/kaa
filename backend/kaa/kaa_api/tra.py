import requests
import bs4
import re
from kaa_api import beforward as bf
import logging

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}
url = "https://gateway.tra.go.tz/umvvs/"
final_url = 'https://gateway.tra.go.tz/umvvs/Umvvc_result.aspx'
car_url = 'https://www.beforward.jp/toyota/mark-x/bg558249/id/1506853/'
main = "ctl00$MainContent$ddl"
make = f'{main}Make'
model = f'{main}Model'
year = f'{main}Year'
country = f'{main}Country'
fuel = f'{main}Fuel'
engine = f'{main}Engine'
async_post = '__ASYNCPOST'
view_state = '__VIEWSTATE'
event_validation = '__EVENTVALIDATION'
search_btn = 'ctl00$MainContent$btnSearch'
event_targets = [make, model, year, country, fuel, engine]
features = [{'variable': make, 'key': 'make'}, {'variable': model, 'key': 'model'}, {'variable': year, 'key': 'year'},
            {'variable': country, 'key': 'country'}, {'variable': fuel, 'key': 'fuel'},
            {'variable': engine, 'key': 'engine'},
            ]


# car_properties={
#     'make':'TOYOTA',
#     'model':'rumion',
#     'year':'2010',
#     'country':'JAPAN',
#     'fuel':'PETROL',
#     'engine':1490
# }


def filter_model_name(model):
    pass


def filter_chassis(chassis):
    pass


def get_model_value(dict_of_features, search, chassis):
    print(search)
    search = search.replace('-', ' ')
    search = search.lower().split(' ')
    # print(search)
    filtered_model_name = []
    for feature in dict_of_features:
        ls_features = feature['text'].split(' ')
        model_name = ls_features[0]
        if model_name.lower() in search:
            filtered_model_name.append(feature)
    #     TODO: if filtered_model_name length == 1 then return

    filtered_chassis_name = []
    found_chassis = re.search(r'([a-z]+\d+)', chassis, re.I)
    if found_chassis:
        found_chassis_number = found_chassis.group(1)
        print(found_chassis_number)
        for feature in filtered_model_name:
            if re.search(found_chassis_number, feature['text'], re.I):
                print('its appending')
                filtered_chassis_name.append(feature)

    if len(filtered_chassis_name) > 0:
        return filtered_chassis_name[0]['value']
    return filtered_model_name[0]['value']


def make_id(variable):
    v_list = variable.split('$')
    return f'{v_list[1]}_{v_list[2]}'


def make_dict_key(name):
    name = name.lower()
    name = name.replace(":", "")
    name = name.replace("(usd)", "")
    name = name.replace("(tshs)", "")
    return name.replace(" ", "")


def get_viewstate(resp):
    result = re.search(r'__VIEWSTATE\|(/[A-Za-z0-9+/==]+)', resp)
    return result.group(1)


def extract_select(html, variable):
    id = make_id(variable)
    select_tag = parse_html(html, id)[0]
    options_tag = select_tag.contents
    select_options = []
    for option_tag in options_tag:
        if isinstance(option_tag, bs4.element.Tag):
            select_options.append({'text': option_tag.text.strip(), 'value': option_tag['value'].strip()})
    select_options.pop(0)
    return select_options


def convert_to_range(list_of_strings):
    range = []
    for x in list_of_strings:
        try:
            number = int(x)
            range.append(number)
        except ValueError:
            continue
    return range


def in_range(range, feature):
    if len(range) == 1:
        if feature >= range[0]:
            return True
    elif len(range) == 2:
        if feature >= range[0] and feature <= range[1]:
            return True


def get_feature_value(html, feature, feature_variable, chassis=None):
    dict_of_features = extract_select(html, feature_variable)
    if feature_variable == model:
        return get_model_value(dict_of_features, feature, chassis)
    else:
        for x in dict_of_features:
            if feature_variable == engine:
                list_of_strings = x['text'].split(' ')
                # print(list_of_strings)
                range = convert_to_range(list_of_strings)
                # print(range)
                if in_range(range, int(feature)):
                    print(x['text'])
                    return x['value']

            else:
                if re.search(feature, x['text'], re.I):
                    print(x['text'])
                    return x['value']
    print(f"{feature_variable} {feature} not Present in TRA database")
    exit()


def get_eventvalidation(resp):
    result = re.search(r'__EVENTVALIDATION\|(/[A-Za-z0-9+/==]+)', resp)
    return result.group(1)


def parse_html(html, id):
    soup = bs4.BeautifulSoup(html, 'lxml')
    return soup.find_all(id=id)


def prepare_form_data(feature_variable, view_state_value, event_validation_value, make_value, model_value=0,
                      year_value=0, country_value=0, fuel_value=0, engine_value=0):
    search = ''
    if engine_value:
        search = 'Calculate'
    return {
        make: make_value,
        model: model_value,
        year: year_value,
        country: country_value,
        fuel: fuel_value,
        engine: engine_value,
        async_post: 'true',
        'ctl00$ctl08': f'ctl00$MainContent$ddlPanel|{feature_variable}',
        '__EVENTTARGET': feature_variable,
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        view_state: view_state_value,
        '__VIEWSTATEGENERATOR': '1EBDE8B9',
        event_validation: event_validation_value,
        search_btn: search
    }


def get_record_details(resp, car):
    resp = parse_html(resp, 'MainContent_UmvvcRecordDetails')
    all_tr = resp[0].find_all('tr')
    td_values = {}
    # print(all_tr)
    for tr in all_tr:
        all_td = tr.find_all('td')
        if len(all_td) == 2:
            td_values[make_dict_key(all_td[0].text)] = all_td[1].text
    td_values['image'] = car['image']
    td_values['rengine'] = car['engine']
    td_values['price'] = add_commas(car['price'])
    td_values['grandtotal'] = add_commas(
        float(car['price']) + float(td_values['totaltaxes'].replace('\n', '').replace(',', '')))

    return td_values


def add_commas(number):
    number = int(number)
    return ("{:,}".format(number))


def main(car_url):
    car_properties = bf.get_car_props(car_url)

    s = requests.Session()
    resp = s.get(url, headers=headers)
    eventvalidation_tag = parse_html(resp.text, event_validation)[0]
    eventvalidation_value = eventvalidation_tag['value']
    viewstate_tag = parse_html(resp.text, view_state)[0]
    viewstate_value = viewstate_tag['value']
    make_value = get_feature_value(resp.text, car_properties['make'], make)
    # refactor
    form_data = prepare_form_data(make, viewstate_value, eventvalidation_value, make_value)
    resp2 = s.post(url, data=form_data, headers=headers)
    eventvalidation_value = get_eventvalidation(resp2.text)
    viewstate_value = get_viewstate(resp2.text)
    model_value = get_feature_value(resp2.text, car_properties['model'], model, car_properties['chassis'])

    form_data = prepare_form_data(model, viewstate_value, eventvalidation_value, make_value, model_value)
    resp3 = s.post(url, data=form_data, headers=headers)
    eventvalidation_value = get_eventvalidation(resp3.text)
    viewstate_value = get_viewstate(resp3.text)
    year_value = get_feature_value(resp3.text, car_properties['year'], year)

    form_data = prepare_form_data(model, viewstate_value, eventvalidation_value, make_value, model_value, year_value)
    resp4 = s.post(url, data=form_data, headers=headers)
    eventvalidation_value = get_eventvalidation(resp4.text)
    viewstate_value = get_viewstate(resp4.text)
    country_value = get_feature_value(resp4.text, car_properties['country'], country)

    form_data = prepare_form_data(model, viewstate_value, eventvalidation_value, make_value, model_value, year_value,
                                  country_value)
    resp5 = s.post(url, data=form_data, headers=headers)
    eventvalidation_value = get_eventvalidation(resp5.text)
    viewstate_value = get_viewstate(resp5.text)
    fuel_value = get_feature_value(resp5.text, car_properties['fuel'], fuel)

    form_data = prepare_form_data(model, viewstate_value, eventvalidation_value, make_value, model_value, year_value,
                                  country_value, fuel_value)
    resp6 = s.post(url, data=form_data, headers=headers)
    eventvalidation_value = get_eventvalidation(resp6.text)
    viewstate_value = get_viewstate(resp6.text)
    engine_value = get_feature_value(resp6.text, car_properties['engine'], engine)

    # end refactor
    form_data = prepare_form_data(model, viewstate_value, eventvalidation_value, make_value, model_value, year_value,
                                  country_value, fuel_value, engine_value)
    resp7 = s.post(url, data=form_data, headers=headers)
    resp8 = s.get(final_url, headers=headers)
    return get_record_details(resp8.text, car_properties)
