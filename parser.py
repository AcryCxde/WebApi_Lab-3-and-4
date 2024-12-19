import requests
from bs4 import BeautifulSoup as Bs
from models import Item

URL = 'https://melomania.online/store/apparatura/'


def fetch_page(url):
    """Извлекает содержимое страницы по-указанному URL-адресу."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Bs(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return None


def get_page_count():
    """Получает общее количество страниц."""
    page = fetch_page(URL)
    if not page:
        print("Не удалось получить страницу для подсчёта элементов.")
        return 0
    count_element = page.find(class_='uss_page_count')
    if count_element:
        return int(count_element.text.replace('Всего: ', ''))
    print("Элемент с количеством страниц не найден.")
    return 0


def find_items(page):
    """Находит названия альбомов и их цены на указанной странице."""
    if not page:
        return []

    all_names = page.findAll(class_='uss_shop_name')
    all_prices = page.findAll(class_='price_class')

    items = []
    for name, price in zip(all_names, all_prices):
        try:
            items.append(Item(
                name=name.text.strip(),
                price=int(price.text.replace(' ', '').strip())
            ))
        except ValueError:
            print(f"Ошибка при обработке элемента: {name.text} - {price.text}")

    return items


def get_data():
    """Извлекает данные со всех страниц."""
    page_count = get_page_count()
    if page_count == 0:
        return []

    data = []
    for i in range(1, (page_count // 21) + 2):
        page_url = f'{URL}?page={i}'
        page = fetch_page(page_url)
        data += find_items(page)

    return data
