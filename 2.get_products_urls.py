from bs4 import BeautifulSoup
import os
from tqdm import tqdm


path = "./category_pages"

# CREATE FILE WITH FINISHED LINKS IF NOT EXISTS
with open('products_pages/finished_products.txt', 'a', encoding='utf-8') as ff:
    ff.close()

# WRITE PRODUCT URL TO FILE
def url_writer(url: str) -> None:
    with open('products_pages/products_urls.csv', 'a', encoding='utf-8') as file:
        file.write("https://sbermegamarket.ru"+ url+'\n')
        file.close()

# SCRAP PRODUCT URLS FROM CATEGORY HTML PAGE
def urls_get(file: str, data: str, ff, dst_file) -> None:
    with open(f'category_pages_duplicate/{file}', 'r', encoding='utf-8') as src:
        soup = BeautifulSoup(src.read(), features='html.parser')
        products = soup.find_all('a', class_='item-image-block ddl_product_link')
        for product in products:
            try:
                url = product.get('href')
                if not url in data:
                    dst_file.write("https://sbermegamarket.ru"+ url+'\n')
                    ff.write(url + '\n')
                    print(product.get('href'))
                else:
                    print('Link already added: ', url)
            except Exception as e:
                print(url, e)
    src.close()


def main() -> None:
    list_of_files = os.listdir(path)
    with open('products_pages/products_urls.csv', 'a', encoding='utf-8') as dst_file:
        for file in tqdm(list_of_files):
            with open('products_pages/finished_products.txt', 'r+', encoding='utf-8') as ff:
                data = ff.read()
                urls_get(file, data, ff, dst_file)
        ff.close()
        dst_file.close()


if __name__ == '__main__':
    main()



