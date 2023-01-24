import csv
import os
from selectolax.parser import HTMLParser


path = "./products_pages"
csv_file_name = 'sbermegamarket.csv'

# CREATE CSV FILE
def create_csv(csv_file_name: str, order: list[str]) -> None:
    with open(csv_file_name, 'w', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=order).writeheader()

# WRITE DATA TO CSV FILE
def write_csv(csv_file_name: str, data: dict) -> None:
    with open(csv_file_name, 'a', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=list(data)).writerow(data)

# SCRAP DATA FROM PRODUCT PAGES
def get_data(page: str) -> None:
    tree = HTMLParser(page)
    title = tree.css_first('.pdp-header').css_first('span').text()
    print(title)
    data = {'name': 'Имя товара', 'value': title}
    write_csv(csv_file_name, data)
    category = tree.css('.breadcrumb-item')
    category_text = ''
    for i in category:
        category_text += i.css_first('span').text()+"/"
    print(category_text)
    data = {'name': 'Товарная группа', 'value': category_text}
    write_csv(csv_file_name, data)
    params_table = tree.css('.pdp-specs__item')
    for row in params_table:
        name = row.css_first('.pdp-specs__item-name').text().strip()
        value = row.css_first('.pdp-specs__item-value').text().strip()
        if 'Код товара' in name:
            sku = value
        if 'Бренд' in name:
            brand = value
        data = {'name': name, 'value': value}
        print(data)
        write_csv(csv_file_name, data)

    data = {'name': 'Бренд', 'value': brand}
    write_csv(csv_file_name, data)
    data = {'name': 'SKU(ID)', 'value': sku}
    write_csv(csv_file_name, data)
    for x in range(0, 2):
        data = {'=': '='}
        write_csv('sbermegamarket.csv', data)


def main():
    order = ['name', 'value']
    create_csv(csv_file_name, order)
    for root, subdirectories, files in os.walk(path):
        for file in files:
            print(file)
            if not 'finished_products' in file and not 'products_urls' in file:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as file:
                    page = file.read()
                    get_data(page)


if __name__ == '__main__':
    main()