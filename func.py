import re
from pprint import pprint

import requests
from fast_bitrix24 import Bitrix

import func_1c
from keys import WEBHOOK

# замените на ваш вебхук для доступа к Bitrix24
webhook = WEBHOOK
b = Bitrix(webhook)


def user_get(user_id: int):
    """Получает юзера из б24 по ID"""
    user = b.call('user.get', {
        'ID': user_id,
        'ADMIN_MODE': 'True'
    })
    return user


def get_company_rq_list(company_id):
    try:
        rq = b.call('crm.requisite.list', {'filter': {'ENTITY_ID': company_id, 'ENTITY_TYPE_ID': '4'}})
        if isinstance(rq,list) and ('ENTITY_ID' in rq[0]):
              rq=rq[0]
    except:
        rq = []
    return rq


def user_get_domain_login(id):
    """Получает Доменный логин пользователя"""
    params = {'ID': id}
    headers = {'Accept': 'application/json'}
    response = requests.get('https://orgtraid.ru/local/php/user.php', params=params, headers=headers)
    # Проверка статуса ответа
    if response.status_code == 200:
        # Регулярное выражение для поиска логина
        pattern = r"\[LOGIN\] => (\S+)"
        match = re.search(pattern, response.text)
        if match:
            # Извлечение и печать логина
            login = match.group(1)
        return login
    else:
        return response.status_code


class Company:
    """
    Компания в Б24
    При инициализации, обновляет поле GUID, если не заполнено
    """

    def __init__(self, id):
        self.id = id
        self.data = b.call('crm.company.get', {'id': self.id})
        self.guid = self.data['UF_CRM_1700513351']
        self.kpp = self.data['UF_CRM_1700522340677']
        self.inn = self.data['UF_CRM_1690987965649']
        if not self.guid:
            self.guid = '00000000-0000-0000-0000-000000000000'
            self.data['UF_CRM_1700513351'] = self.guid
            self.company_guid_update()


    def check_1c(self):
        """Проверка компании в 1С"""
        guid = func_1c.company_add_or_get(inn=self.inn, kpp=self.kpp, create='0')['#value'][0]['#value']
        return guid

    def add_1c(self):
        """Создание компании в 1С"""
        pass

    def company_update(self):
        """Обновление компании в битриксе
        на вход принимает объект self.data
        """
        upd_data = self.data
        address_keys = [key for key in upd_data.keys() if
                        key.startswith('ADDRESS_') or key.startswith('REG_ADDRESS_')  or key.startswith('REG_ADDRESS')]
        for key in address_keys:
            del upd_data[key]
        pprint(upd_data)
        upd = b.call(
            'crm.company.update',
            {
                'id': self.id,
                'fields': self.data
            }
        )
    def company_guid_update(self):
        upd = b.call('crm.company.update', {
            'id':self.id,
            'fields': {
                'UF_CRM_1690987965649': self.guid
            }
        })
