import requests
from bs4 import BeautifulSoup
import json

url = "https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=489022"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    content = response.text
    print(content)
else:
    print("Failed to retrieve the content. Status code:", response.status_code)



# Создаем объект BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Находим таблицу с классом "table-character"
table = soup.find('table', class_='table-character')

# Создаем пустой словарь для хранения данных
data = {}

# Итерируемся по строкам таблицы
for row in table.find_all('tr'):
    text = row.find('td', class_='table-character-text').text
    value = row.find('td', class_='table-character-value').text
    # Декодируем текст из UTF-8
    text = text.encode('utf-8').decode('utf-8')
    value = value.encode('utf-8').decode('utf-8')
    data[text] = value

# Преобразуем словарь в JSON
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Выводим JSON-данные
print(json_data)