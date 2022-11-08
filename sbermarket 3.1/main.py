import datetime
import os
from tqdm import tqdm

from selenium.common import NoSuchElementException, exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config.conf import path
from config.dev_conf import INPUT, OUTPUT
from libs.file_work import writeDataToCSV, read_file
from libs.selenium import init_driver, safe_get, does_element_exist, scroll

arr = read_file(os.path.join(INPUT, path))

category_urls = [(store['sid'], store['url'], store["category"], store["subCategory"]) for store in arr]

driver = init_driver()

wait = WebDriverWait(driver, 10)
ac = ActionChains(driver)
all_data = []

for category_url in category_urls:
    sid, url, category, subCategory = category_url

    if not safe_get(driver, url):
        print('Не удалось установить соединение.')
        continue

    locator = (By.XPATH, '//div[@class="ProductCard_styles_root__7ol6i"]')
    window = (By.CLASS_NAME, 'styles_root__weSy4')

    if does_element_exist(wait, window):
        years = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div[2]/button')
        driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div[2]/div[5]/label/input').click()
        ac.move_to_element(years).click().perform()

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Image_root__QyHLt')))
        except (exceptions.TimeoutException, exceptions.StaleElementReferenceException):
            continue

    print(f'Собираем данные с ссылки: {url}.')

    info = [*category_url]

    scroll(driver)

    products = driver.find_elements(*locator)

    pbar = tqdm(products[::-1])
    for product in pbar:
        pbar.set_description('Загружено')
        data = [*info]

        ac.move_to_element(product).perform()

        try:
            name = product.find_element(By.CLASS_NAME, 'ProductCard_styles_title__0noWn').text
            data.append(name)
        except NoSuchElementException:
            data.append('')

        try:
            href = product.find_element(By.CLASS_NAME, 'Link_root__iJUtm').get_attribute('href')
            data.append(href)
        except NoSuchElementException:
            data.append('')

        try:
            fake_price = \
                product.find_element(By.CLASS_NAME, 'ProductCardPrice_styles_originalPrice__O2PgD').text.split('\n')[
                    1].strip()
            data.append(fake_price)
        except NoSuchElementException:
            data.append('')

        try:
            price = product.find_element(By.CLASS_NAME, 'ProductCardPrice_styles_price__NCcXq').text.split('\n')[
                1].strip()
            data.append(price)
        except NoSuchElementException:
            data.append('')

        try:
            date = product.find_element(By.CLASS_NAME, 'PromoBadge_info__1GFt9').text
            data.append(date)
        except NoSuchElementException:
            data.append('')

        try:
            quantity = product.find_element(By.CLASS_NAME, 'ProductCard_styles_volume__LYMZk').text
            data.append(quantity)
        except NoSuchElementException:
            data.append('')

        all_data.append(data)

headers = ['sid', 'Ссылка категории', 'Категория 1-ого уровня', 'Категория 2-ого уровня', 'Наименование товара',
           'Ссылка на товар', 'Старая цена', 'Цена', 'Срок окончания Акции', 'Информация о товаре']
date = datetime.datetime.now().strftime('%H-%M-%Y-%m-%d')
writeDataToCSV(os.path.join(OUTPUT, f'sber-{date}.csv'), headers, all_data)
print('Данные собраны!')
