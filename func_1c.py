from pprint import pprint

import requests

from keys import base64_auth_string


def get_1c_guid(inn, kpp):
    """Получаем 1С ГУИД"""
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/counterparty"

    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }

    data = {
        "#type": "jv8:Structure",
        "#value": [
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "ИНН"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": inn
                }
            },
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "КПП"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": kpp
                }
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        # Возвращаем только первый UUID из ответа
        return response.json()["#value"][0]["#value"]
    else:
        return None  # Возвращаем None в случае ошибки


def get_1c_user_guid(user_login):
    """Получаем гуид пользователя """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Sotrudniki"

    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }

    data = {"#type": "jv8:Structure",
            "#value": [{
                "name": {"#type": "jxs:string",
                         "#value": "AD_Аутентификация"},
                "Value": {"#type": "jxs:string",
                          "#value": f"\\\\TRKTK\\{user_login}"}
            }]
            }
    datafix2005 = {"#type": "jv8:Structure",
                        "#value": [{
                            "name": {"#type": "jxs:string",
                                     "#value": "AD_Аутентификация"},
                            "Value": {"#type": "jxs:string",
                                      "#value": "\\\\TRKTK\\ponomarev.av"}
                        }]
                        }
    data20052024={
        "#type": "jv8:Structure",
        "#value": [
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "AD_Аутентификация"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": "\\\\trktk\\zykin.sv"
                }
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    response_txt = response.json()
    pprint({
        'Вход': data,
        'Выход': response_txt
    })
    return response_txt['#value'][0]['Value']['#value']


def company_add_or_get(inn='',
                       kpp='',
                       guid='00000000-0000-0000-0000-000000000000',
                       create='1',
                       id_bitrix='',
                       name='',
                       full_name='',
                       short_name='',
                       entity_type='entity',
                       phone='',
                       email='',
                       last_name='',
                       first_name='',
                       middle_name=''):
    """Получаем ГУИД компании из 1С.
    Если нужно создать компанию, передаем create=1, для поиска компании, передаем create=0"""
    """Получаем 1С ГУИД"""
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/counterparty"
    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    data = {
        "#type": "jv8:Structure",
        "#value": [
            {"name": {"#type": "jxs:string", "#value": "ИНН"}, "Value": {"#type": "jxs:string", "#value": inn}},
            {"name": {"#type": "jxs:string", "#value": "КПП"}, "Value": {"#type": "jxs:string", "#value": kpp}},
            {"name": {"#type": "jxs:string", "#value": "GUID"}, "Value": {"#type": "jxs:string", "#value": guid}},
            {"name": {"#type": "jxs:string", "#value": "Создать"}, "Value": {"#type": "jxs:string", "#value": create}},
            {"name": {"#type": "jxs:string", "#value": "ИДБитрих"},
             "Value": {"#type": "jxs:string", "#value": id_bitrix}},
            {"name": {"#type": "jxs:string", "#value": "Наименование"},
             "Value": {"#type": "jxs:string", "#value": name}},
            {"name": {"#type": "jxs:string", "#value": "НаименованиеПолное"},
             "Value": {"#type": "jxs:string", "#value": full_name}},
            {"name": {"#type": "jxs:string", "#value": "НаименованиеСокращенное"},
             "Value": {"#type": "jxs:string", "#value": short_name}},
            {"name": {"#type": "jxs:string", "#value": "ТипКонтрагента"},
             "Value": {"#type": "jxs:string", "#value": entity_type}},
            {"name": {"#type": "jxs:string", "#value": "Телефон"}, "Value": {"#type": "jxs:string", "#value": phone}},
            {"name": {"#type": "jxs:string", "#value": "ЭлПочта"}, "Value": {"#type": "jxs:string", "#value": email}},
            {"name": {"#type": "jxs:string", "#value": "Фамилия"},
             "Value": {"#type": "jxs:string", "#value": last_name}},
            {"name": {"#type": "jxs:string", "#value": "Имя"}, "Value": {"#type": "jxs:string", "#value": first_name}},
            {"name": {"#type": "jxs:string", "#value": "Отчество"},
             "Value": {"#type": "jxs:string", "#value": middle_name}},
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    pprint({
        'Вход': data,
        'Выход': response.json()
    })
    return response.json()


def contract_add(
        create='1',  # Создать
        guid='00000000-0000-0000-0000-000000000000',  # ГУИД Договора
        bitrix_id='11',  # Bitrix id
        name='Договор (продажа) № ЦК001377 от 29.12.21',  # Наименование
        organization_guid='3884dad3-a9c2-11e7-94c4-525400dfd4c5',  # ГУИД Организации
        counterparty_guid='3a3c9b68-8a0e-11ee-80f8-00155d070a01',  # ГУИД Контрагента
        contract_type='Продажа',  # Вид Договора
        start_date='20230101',  # Дата Начала
        end_date='20231231',  # Дата Окончания
        auto_prolongation='0',  # Автопролонгация
        service='1',  # Сервис
        responsible_manager_guid='3e66be72-c8d3-11e9-90fc-901b0ef3f916',  # ГУИД Ответственного Менеджера
        prepayment_percentage='100',  # Процент Предоплаты
        loan_amount='1000000',  # Сумма Кредита
        payment_term='30',  # Срок Оплаты
        comment='тест комментарий',  # Комментарий
        contract_number='ЦК001377',  # Номер Договора
        currency='643'  # Валюта

):
    """
    Создаем Договор в 1С
    """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Contract"

    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }

    data = {
        "#type": "jv8:Structure",
        "#value": [
            {"name": {"#type": "jxs:string", "#value": "Создать"}, "Value": {"#type": "jxs:string", "#value": create}},

            {"name": {"#type": "jxs:string", "#value": "GUID_Договора"},
             "Value": {"#type": "jxs:string", "#value": guid}},

            {"name": {"#type": "jxs:string", "#value": "ИДБитрих"},
             "Value": {"#type": "jxs:string", "#value": bitrix_id}},

            {"name": {"#type": "jxs:string", "#value": "Наименование"},
             "Value": {"#type": "jxs:string", "#value": name}},

            {"name": {"#type": "jxs:string", "#value": "GUID_Организация"},
             "Value": {"#type": "jxs:string", "#value": organization_guid}},

            {"name": {"#type": "jxs:string", "#value": "GUID_Контрагент"},
             "Value": {"#type": "jxs:string", "#value": counterparty_guid}},

            {"name": {"#type": "jxs:string", "#value": "ВидДоговора"},
             "Value": {"#type": "jxs:string", "#value": contract_type}},

            {"name": {"#type": "jxs:string", "#value": "ДатаНачала"},
             "Value": {"#type": "jxs:string", "#value": start_date}},

            {"name": {"#type": "jxs:string", "#value": "ДатаОкончания"},
             "Value": {"#type": "jxs:string", "#value": end_date}},

            {"name": {"#type": "jxs:string", "#value": "Автопролонгация"},
             "Value": {"#type": "jxs:string", "#value": auto_prolongation}},

            {"name": {"#type": "jxs:string", "#value": "Сервис"},
             "Value": {"#type": "jxs:string", "#value": service}},

            {"name": {"#type": "jxs:string", "#value": "GUID_ОтветственныйМенеджер"},
             "Value": {"#type": "jxs:string", "#value": responsible_manager_guid}},

            {"name": {"#type": "jxs:string", "#value": "ПроцентПредоплаты"},
             "Value": {"#type": "jxs:string", "#value": prepayment_percentage}},

            {"name": {"#type": "jxs:string", "#value": "СуммаКредита"},
             "Value": {"#type": "jxs:string", "#value": loan_amount}},

            {"name": {"#type": "jxs:string", "#value": "СрокОплаты"},
             "Value": {"#type": "jxs:string", "#value": payment_term}},

            {"name": {"#type": "jxs:string", "#value": "Комментарий"},
             "Value": {"#type": "jxs:string", "#value": comment}},

            {"name": {"#type": "jxs:string", "#value": "НомерДоговора"},
             "Value": {"#type": "jxs:string", "#value": contract_number}},

            {"name": {"#type": "jxs:string", "#value": "Валюта"},
             "Value": {"#type": "jxs:string", "#value": currency}}
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    response_txt = response.json()
    pprint({
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': response_txt
    })
    return response.json()


def contract_upd(
        guid='00000000-0000-0000-0000-000000000000',  # ГУИД Договора
        shipment_state=False # Значение для поля `Сделки запрещены`

):
    """
    Разрешаем отгрузки по договору 1С
    """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Contract"

    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    shipment = '1'

    if shipment_state:
        shipment = '1'
    else:
        shipment = '0'
    data = {
        "#type": "jv8:Structure",
        "#value": [
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "Создать"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": "2"
                }
            },
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "GUID_Договора"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": guid,
                }
            },
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "СтруктураРеквизитовКИзменению"
                },
                "Value": {
                    "#type": "jv8:Structure",
                    "#value": [
                        {
                            "name": {
                                "#type": "jxs:string",
                                "#value": "СделкиЗапрещены"
                            },
                            "Value": {
                                "#type": "jxs:string",
                                "#value": shipment
                            }
                        },
                    ]
                }
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    response_txt = response.json()
    pprint({
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': response_txt
    })
    return response.json()


def contract_get(
        guid='00000000-0000-0000-0000-000000000000',  # ГУИД Договора

):
    """
    Ищем договор в  1С
    """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Contract"

    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }

    data = {
        "#type": "jv8:Structure",
        "#value": [
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "Создать"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": "0"
                }
            },
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "GUID_Договора"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": guid,
                }
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    response_txt = response.json()
    pprint({
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': response_txt
    })
    return response.json()


def company_shipment_update(guid, shipment: bool):
    """Разрешаем или запрещаем отгрузки по контрагенту
    Если надо разрешить отгрузку shipment=0
    Если надо запретить отгрузку shipment=1
    """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/counterparty"
    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    data = {
        "#type": "jv8:Structure",
        "#value": [
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "Создать"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": "2"
                }
            },
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "GUID"
                },
                "Value": {
                    "#type": "jxs:string",
                    "#value": guid,
                }
            },
            # {
            #   "name": {
            #     "#type": "jxs:string",
            #     "#value": "ИДБитрих"
            #   },
            #   "Value": {
            #     "#type": "jxs:string",
            #     "#value": ""
            #   }
            # },
            {
                "name": {
                    "#type": "jxs:string",
                    "#value": "СтруктураРеквизитовКИзменению"
                },
                "Value": {
                    "#type": "jv8:Structure",
                    "#value": [
                        {
                            "name": {
                                "#type": "jxs:string",
                                "#value": "СделкиЗапрещены"
                            },
                            "Value": {
                                "#type": "jxs:string",
                                "#value": str(shipment),
                            }
                        }
                    ]
                }
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    print(response)
    try:
        response_txt = response.json()
    except Exception as e:
        response_txt = e
    pprint({
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': [response.status_code, response_txt],
    })

def check_1c_company_shipment_status(guid:str):
    """Получает текущее значение разрешения на отгрузку из 1С
    Если 1 - значит отгрузки запрещены
    Если 0 - значит отгрузки разрешены
    """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Spisocdan"
    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    data = {
      "ОбъектМетаданных": "Справочник.Контрагенты",
      "МассивРеквизитов": [
        # "Наименование",
        # "Автор",
        "СделкиЗапрещены"
      ],
      "Отбор": {
        "СписокСсылка": [
          guid
        ]
      }
    }
    response = requests.post(url, json=data, headers=headers)
    print(response)
    try:
        response_txt = response.json()
    except Exception as e:
        response_txt = e
    pprint({
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': [response.status_code, response_txt],
    })
    res = response_txt['#value'][0]['#value']
    value = None
    for item in res:
        if item['name']['#value'] == 'СделкиЗапрещены':
            value = item['Value']['#value']
            break
    # pprint({
    #     'url': response.url,
    #     'headers': headers,
    #     'Вход': data,
    #     'Выход': [response.status_code, response_txt],
    #     'Возвращаемое значнеие': value,
    # })
    return value
def check_1c_contract_shipment_status(guid:str):
    """Получает текущее значение разрешения на отгрузку из 1С
    Объект - Договор
    Если 1 - значит отгрузки запрещены
    Если 0 - значит отгрузки разрешены
    """
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Spisocdan"
    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    data = {
      "ОбъектМетаданных": "Справочник.ДоговорыВзаиморасчетов",
      "МассивРеквизитов": [
        # "Наименование",
        # "Автор",
        "СделкиЗапрещены"
      ],
      "Отбор": {
        "СписокСсылка": [
          guid
        ]
      }
    }
    response = requests.post(url, json=data, headers=headers)
    # print(response)
    try:
        response_txt = response.json()
    except Exception as e:
        response_txt = e
    # print(response_txt)
    res = response_txt['#value'][0]['#value']
    value = None
    for item in res:
        if item['name']['#value'] == 'СделкиЗапрещены':
            value = item['Value']['#value']
            break
    # pprint({
    #     'url': response.url,
    #     'headers': headers,
    #     'Вход': data,
    #     'Выход': [response.status_code, response_txt],
    #     'Возвращаемое значнеие': value,
    # })
    return value

def get_all_1c_contract_fields():
    """Отдает все поля сущности договор"""
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Spisocdan"
    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    data = {
        "ОбъектМетаданных": "Справочник.ДоговорыВзаиморасчетов",
        "ПолучитьРеквизитыОбъекта": "",
    }
    response = requests.post(url, json=data, headers=headers)
    # print(response)
    try:
        response_txt = response.json()
    except Exception as e:
        response_txt = e
    result = {
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': [response.status_code, response_txt],
    }
    return result


def get_all_1c_company_fields():
    """Отдает все поля сущности компания"""
    url = "http://10.12.225.123/aa4/hs/trktk_bitrix/Spisocdan"
    headers = {
        "Authorization": f"Basic {base64_auth_string}"
    }
    data = {
        "ОбъектМетаданных": "Справочник.Контрагенты",
        "ПолучитьРеквизитыОбъекта": "",
    }
    response = requests.post(url, json=data, headers=headers)
    # print(response)
    try:
        response_txt = response.json()
    except Exception as e:
        response_txt = e
    result = {
        'url': response.url,
        'headers': headers,
        'Вход': data,
        'Выход': [response.status_code, response_txt],
    }
    return result