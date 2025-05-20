import requests
from bs4 import BeautifulSoup

def parse_table(doc_url):
    response = requests.get(doc_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')

    table = tables[0]
    parsed_data = []
    for row in table.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        parsed_data.append([cell.get_text(strip=True) for cell in cells])

    return parsed_data


url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"
tb = parse_table(url)


def print_result(data):
    max_x = 0
    max_y = 0
    for i in range(1, len(data)):
        max_x = max(int(data[i][0]), max_x)
        max_y = max(int(data[i][2]), max_y)
    
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    for i in range(1, len(data)):
        x, y, char = int(data[i][0]), int(data[i][2]), data[i][1]
        grid[max_y - y][x] = char  

    for row in grid:
        print(''.join(row))
       
print_result(tb)
