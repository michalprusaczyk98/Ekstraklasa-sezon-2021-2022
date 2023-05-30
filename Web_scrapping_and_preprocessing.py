#pip install BeautifulSoup4
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import csv
import os

data = {
    'name': [],
    'data of birth': [],
    'height': [],
    'foot': [],
    'joined': [],
    'contract until': [],
}


# request to transfermarkt


headers = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

#url of team
url = "https://www.transfermarkt.pl/ac-milan/kader/verein/5/saison_id/2022/plus/1"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')


# Filter and data parsing


all_tr = soup.find_all('tr', {'class': ['odd', 'even']})
td_element = soup.find_all('td', {'class': ['zentriert']})

club_name = soup.find_all('div', {'class': ['data-header__profile-container']})[0].find('img')['title']



# data parsing for nationality
countries = []
for i in range(len(td_element)):
    if td_element[i].find('img', {'class': 'flaggenrahmen'}) is None:
        continue
    
    if len(td_element[i].find_all('img', {'class': 'flaggenrahmen'})) == 2:
        countries.append(td_element[i].find_all('img', {'class': 'flaggenrahmen'})[0]['title'] 
                         + " / " + td_element[i].find_all('img', {'class': 'flaggenrahmen'})[1]['title'])
    else:
        countries.append(td_element[i].find('img')['title'])

        


# data parsing for another infos


for row in all_tr:
    all_td = row.find_all('td', recursive=False)
    data['name'].append( all_td[1].text.split('.')[0][:-1] )
    data['data of birth'].append( all_td[2].text[:-5] )
    data['height'].append( all_td[4].text )
    data['foot'].append( all_td[5].text )
    data['joined'].append( all_td[6].text )
    data['contract until'].append( all_td[8].text )

df = pd.DataFrame(data)

#changing dictionary type to ndarray

data_keys = data.keys()


new_2d_arr = np.array([data[i] for i in data_keys])


trans = np.transpose(new_2d_arr)

#creating a dataset which do not need to clean
cleandata = trans[:,1:]

#cleansing first column

split = np.char.split(trans[:,0])

excluded_positions = ["Bramkarz","Środkowy","obrońca","Ofensywny","pomocnik","Defensywny","napastnik","Lewy","Prawy","Cofnięty"]

list_name = []


# gathering names into one column


for row in split:
    combined_name = ' '.join([name for name in row if name not in excluded_positions])
    list_name.append(combined_name)

name = np.chararray.strip(list_name)

# gathering positions ino another column

list_position = [[x for x in row if x in excluded_positions] for row in split]

new_list_position = []

for item in list_position:
    if type(item) == list:
        if len(item) == 2:
            new_item = ' '.join(item)
            new_list_position.append(new_item)
        else:
            new_list_position.extend(item)
        
    
position = np.array(new_list_position)

# Creating a column with club name of every football player in team which we are data preprocessing


club = [club_name] * len(name)

cleaned_data = np.column_stack((name, new_list_position,countries, cleandata,club))
df = pd.DataFrame(cleaned_data)

header_columns = ["Imie i Nazwisko","Pozycja","Narodowość","Rok urodzenia","Wzrost","Lepsza noga","W drużynie od","Kontrakt", "Klub"]


directory_file_csv = os.path.join(os.getcwd(), "club_data.csv")

if os.path.isfile(directory_file_csv):
    df.to_csv('club_data.csv', mode='a', index=False, header=False)
else:
    df.to_csv("club_data.csv", index = False)


#remove = pd.read_csv('club_data.csv')
#remove = remove.drop(remove.index[93:])
#remove.to_csv('club_data.csv')
#pd.options.display.max_columns = None
#pd.options.display.max_rows = None

data = pd.read_csv("club_data.csv")
data.columns = header_columns
data
