import json
import requests
from time import sleep
from typing import Optional
from settings import token  # OAuth-токен Яндекс.Диска


class YD:
    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_name: str) -> bool:
        """Создаёт папку на Яндекс.Диске. Возвращает True, если успешно."""
        url = f'{self.base_url}/v1/disk/resources'
        params = {'path': folder_name}
        response = requests.put(url, headers=self.headers, params=params, timeout=10)

        # 201 — создано, 409 — уже существует (считаем успехом)
        if response.status_code in (201, 409):
            print(f'Папка "{folder_name}" готова.')
            return True

        print(f'Ошибка создания папки: {response.status_code} — {response.text}')
        return False

    def upload_file(self, path_to_file: str, path_to_disk: str) -> bool:
        """Загружает локальный файл на Яндекс.Диск. Возвращает True, если успешно."""
        url = f'{self.base_url}/v1/disk/resources/upload'
        params = {'path': path_to_disk, 'overwrite': 'true'}
        response = requests.get(url, headers=self.headers, params=params, timeout=10)

        if response.status_code != 200:
            print(f'Ошибка получения ссылки для загрузки: {response.status_code} — {response.text}')
            return False

        upload_url = response.json().get('href')
        if not upload_url:
            print('Не получили ссылку для загрузки.')
            return False

        with open(path_to_file, 'rb') as f:
            upload_resp = requests.put(upload_url, data=f, timeout=30)

        if upload_resp.status_code in (200, 201):
            print(f'Файл "{path_to_file}" загружен на диск как "{path_to_disk}".')
            return True

        print(f'Ошибка загрузки файла: {upload_resp.status_code}')
        return False


class LocationFinder:
    def __init__(self, ipify_url: str = 'https://api.ipify.org',
                 ipinfo_template: str = 'https://ipinfo.io/{}/geo'):
        self.ipify_url = ipify_url
        self.ipinfo_template = ipinfo_template
        self.my_ip: Optional[str] = None
        self.city: Optional[str] = None

    def fetch_ip(self, timeout: int = 5) -> bool:
        """Получает IP-адрес через api.ipify.org."""
        try:
            response = requests.get(self.ipify_url, timeout=timeout)
            response.raise_for_status()
            self.my_ip = response.text.strip()
            return True
        except requests.RequestException as e:
            print(f'Ошибка получения IP: {e}')
            return False

    def fetch_city(self, timeout: int = 5) -> bool:
        """Определяет город по IP через ipinfo.io."""
        if not self.my_ip:
            print('IP не получен. Сначала вызовите fetch_ip().')
            return False
        url = self.ipinfo_template.format(self.my_ip)
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            self.city = data.get('city')
            return self.city is not None
        except (requests.RequestException, ValueError) as e:
            print(f'Ошибка получения города: {e}')
            return False

    def save_to_json(self, filename: str = 'location.json') -> bool:
        """Сохраняет IP и город в JSON-файл."""
        data = {
            'ip': self.my_ip,
            'city': self.city,
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'Данные сохранены в {filename}: {data}')
        return True

    def run_full_flow(self):
        """Полный цикл: IP → город → JSON → загрузка на Диск."""
        print('Запрашиваем IP...')
        sleep(2)  # имитация задержки для наглядности
        if not self.fetch_ip():
            print('Не удалось получить IP.')
            return
        print(f'Успешно! Ваш IP: {self.my_ip}')
        sleep(2)

        print('Запрашиваем город...')
        sleep(2)
        if not self.fetch_city():
            print('Город не найден.')
            return
        print(f'Успешно! Ваш город: {self.city}')
        sleep(2)

        print('Сохраняем в JSON...')
        self.save_to_json('location.json')
        sleep(2)

        print('Загружаем на Яндекс.Диск...')
        yd = YD(token)
        yd.create_folder('location_data')
        yd.upload_file('location.json', 'location_data/location.json')


if __name__ == '__main__':
    finder = LocationFinder()
    finder.run_full_flow()





















# import requests
# from settings import token  # твой OAuth-токен Яндекс.Диска
# from time import sleep
# from typing import Optional
#
# class YD:
#     base_url = 'https://cloud-api.yandex.net'
#
#     def __init__(self, token):
#         self.headers = {'Authorization': f'OAuth {token}'}
#
#     def create_folder(self, folder_name: str) -> bool:
#         """Создаёт папку на Яндекс.Диске. Возвращает True, если успешно."""
#         url = f'{self.base_url}/v1/disk/resources'
#         params = {'path': folder_name}
#         response = requests.put(url, headers=self.headers, params=params, timeout=10)
#
#         # 201 — создано, 409 — уже существует (тоже считаем успехом)
#         if response.status_code in (201, 409):
#             print(f'Папка "{folder_name}" готова.')
#             return True
#
#         print(f'Ошибка создания папки: {response.status_code} — {response.text}')
#         return False
#
#     def upload_file(self, path_to_file: str, path_to_disk: str) -> bool:
#         """Загружает локальный файл на Яндекс.Диск. Возвращает True, если успешно."""
#         url = f'{self.base_url}/v1/disk/resources/upload'
#         params = {'path': path_to_disk, 'overwrite': 'true'}
#         response = requests.get(url, headers=self.headers, params=params, timeout=10)
#
#         if response.status_code != 200:
#             print(f'Ошибка получения ссылки для загрузки: {response.status_code} — {response.text}')
#             return False
#
#         upload_url = response.json().get('href')
#         if not upload_url:
#             print('Не получили ссылку для загрузки.')
#             return False
#
#         with open(path_to_file, 'rb') as f:
#             upload_resp = requests.put(upload_url, data=f, timeout=30)
#
#         if upload_resp.status_code in (200, 201):
#             print(f'Файл "{path_to_file}" загружен на диск как "{path_to_disk}".')
#             return True
#
#         print(f'Ошибка загрузки файла: {upload_resp.status_code}')
#         return False
#
# def main():
#     yd = YD(token)
#     yd.create_folder("test")
#     yd.upload_file('image.jpg', 'test')
#
# main()
#
# class LocationFinder:
#     def __init__(self, ipify_url: str = 'https://api.ipify.org',
#                  ipinfo_template: str = 'https://ipinfo.io/{}/geo'):
#         self.ipify_url = ipify_url
#         self.ipinfo_template = ipinfo_template
#         self.my_ip: Optional[str] = None
#         self.city: Optional[str] = None
#
#     def fetch_ip(self, timeout: int = 5) -> bool:
#         """Запрашивает IP и сохраняет в self.my_ip. Возвращает True, если успешно."""
#         try:
#             response = requests.get(self.ipify_url, timeout=timeout)
#             response.raise_for_status()
#             self.my_ip = response.text.strip()
#             return True
#         except requests.RequestException as e:
#             print(f'Ошибка получения IP: {e}')
#             return False
#
#     def fetch_city(self, timeout: int = 5) -> bool:
#         """По сохранённому IP запрашивает город и сохраняет в self.city. Возвращает True, если успешно."""
#         if not self.my_ip:
#             print('IP не получен. Сначала вызовите fetch_ip().')
#             return False
#         url = self.ipinfo_template.format(self.my_ip)
#         try:
#             response = requests.get(url, timeout=timeout)
#             response.raise_for_status()
#             data = response.json()
#             self.city = data.get('city')
#             return self.city is not None
#         except (requests.RequestException, ValueError) as e:
#             print(f'Ошибка получения города: {e}')
#             return False
#
#     def run_full_flow(self):
#         """Выполняет полный цикл: IP → город, с паузами и выводом."""
#         print('Запрашиваем IP...')
#         sleep(2)
#         if not self.fetch_ip():
#             print('Не удалось получить IP.')
#             return
#         print(f'Успешно! Ваш IP: {self.my_ip}')
#         sleep(2)
#
#         print('Запрашиваем город...')
#         sleep(2)
#         if self.fetch_city():
#             print(f'Успешно! Ваш город: {self.city}')
#         else:
#             print('Город не найден.')
#
#
#
#
# if __name__ == '__main__':
#     finder = LocationFinder()
#     finder.run_full_flow()
#
#
#
