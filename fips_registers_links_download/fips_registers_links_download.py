import requests
import re
import json
from datetime import datetime
import os
from pathlib import Path


class FipsRegistersLinksDownloader:

    # страница с перечнем реестров
    url_registers = 'https://new.fips.ru/registers-web/register'
    # страница конкретного реестра
    url_register = 'https://new.fips.ru/registers-web/action?acName=clickRegister&regName=<REG_NAME>'
    # стартовая страница просмотра ссылок реестра
    url_start_page = 'https://new.fips.ru/registers-web/action?acName=clickTree&nodeId=<START_NODEID>&maxLevel=1'
    # ссылка для перехода на следующую страницу
    url_next = 'https://new.fips.ru/registers-web/action?acName=nextPage&direction=-1'
    # ссылка для перехода на предыдущую страницу
    url_prev = 'https://new.fips.ru/registers-web/action?acName=nextPage&direction=1'
    # каталог для скачивания
    downloads_dir = 'downloads'

    def __init__(self, ois_type, **kwargs):
        self.page = None
        self.links = []
        self.ois_type = ois_type
        self.url_register = self.url_register.replace('<REG_NAME>', ois_type)
        self.__init_session()
        self.url_start_page = self.url_start_page.replace("<START_NODEID>", self.start_nodeid)
        # текущее время
        self.start_time = datetime.today()
        # инициализация каталога проекта
        self.project_dir = kwargs.get('project_dir', self.start_time.strftime('%Y-%m-%d'))
        self.project_dir = os.path.join(self.downloads_dir, self.project_dir)
        Path(self.project_dir).mkdir(parents=True, exist_ok=True)
        # имя, под которым будет сохранён файл со ссылками
        self.filename_suffix = kwargs.get('filename_suffix', self.start_time.strftime('%HH-%MM'))
        self.filename_suffix = '-' + self.filename_suffix if len(self.filename_suffix) > 0 else ''
        self.filename = self.ois_type + self.filename_suffix + '.json'

    def download_links(self):
        self.page = self.s.get(self.url_start_page).text
        self.links = self.extract_links()
        i = 0
        while True:
            self.page = self.s.get(self.url_prev).text
            links = self.extract_links()
            go_next = False if "<nobr>Предыдущий диапазон</nobr>" in self.page else True
            if len(links) > 0 and go_next is True:
                self.links += links
                i += 1
            else:
                break
        self.save_links()

    def save_links(self):
        with open(os.path.join(self.project_dir, self.filename), 'w+') as f:
            json.dump(dict(self.links), f)

    @property
    def filepath(self):
        return os.path.join(self.project_dir, self.filename)

    def extract_links(self):
        """Извлекает ссылки"""
        return re.findall(
            r'<a target="_blank" href="(/registers-doc-view/fips_servlet\?DB=' \
            + self.ois_type + '&rn=\d+&DocNumber=(\d+)&TypeFile=html)">\d+</a>',
            self.page)

    @property
    def s(self):
        return self.__s

    def __init_session(self):
        self.__s = requests.Session()
        try:
            # переходим сначала в каталог реестров
            response = self.s.get(self.url_registers)
            self.page = response.text
            # затем на страницу реестра
            response = self.s.get(self.url_register)
            self.page = response.text
            # теперь пытаемся прочитать стартовую страницу для скачивания
            self.start_nodeid = self.__extract_start_node_id()
        except Exception as e:
            raise e

    def __extract_start_node_id(self):
        """Извлекает стартовую страницу для просмотра реестра."""
        try:
            page_text = re.sub(r'\s+', ' ', self.page)
            nodes = re.findall(r'<li>\s*&nbsp;\s*<a href="action\?acName=clickTree&nodeId=('
                               r'\d+)&maxLevel=1"\s+class="red"\s*>(?:\d+)&nbsp;-&nbsp;(?:\d+)</a>\s*</li>', page_text)
        except Exception as e:
            raise Exception("Ошибка извлечения стартовой страницы!") from e
        if len(nodes) >= 1:
            return nodes[0]
        else:
            raise Exception("Не найдено ссылок на стартовую страницу реестра!")