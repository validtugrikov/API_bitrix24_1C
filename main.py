import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import func
import func_1c

import ssl

app = FastAPI()
# app.add_middleware(HTTPSRedirectMiddleware)
#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#ssl_context.load_cert_chain('./cert.pem',
#                            keyfile='./key.pem')


# Для старта приложения
# uvicorn main:app --host 0.0.0.0 --reload


# Создаем логгер с уникальным именем
logger = logging.getLogger('my_custom_logger')
logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования

# Создаем файловый обработчик логирования
file_handler = logging.FileHandler('custom_main.log', mode='w')
file_handler.setLevel(logging.DEBUG)

# Настраиваем форматирование для обработчика
formatter = logging.Formatter('%(asctime)s, %(levelname)s, \n %(message)s, %(name)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)



@app.get("/test/")
async def root():
    res=''
    print('is test')
    # res=user_1c_guid = func_1c.get_all_1c_contract_fields()
    # logger.info(f'Получен 1c GUID юзера -> {user_1c_guid}')
    res=res if bool(res) else 'is.ret...'
    return res

@app.post('/1c/company_add/')
def company_add(company_id):
    """# Создание компании в 1С
    ## Логика работы
    Принимает на вход: ID компании в Б24\n
    """
    try:
        company = func.b.call('crm.company.get', {'id': company_id})
        logger.info(f'Получен запрос на создание компании в 1с {company}')
    except Exception as e:
        logger.exception(f'В б24 нет компании c id {company_id} {e}')
    try:
        ad_login = func.user_get_domain_login(company['ASSIGNED_BY_ID'])
        logger.info(f'Получен ад логин юзера -> {ad_login}')
    except:
        logger.exception(f'не удалось получить ад логин юзера')
    try:
        user_1c_guid = func_1c.get_1c_user_guid(ad_login)
        logger.info(f'Получен 1c GUID юзера -> {user_1c_guid}')
    except:
        logger.exception(f'не удалось 1c GUID юзера')

    req = func.get_company_rq_list(company_id)
    if not req:
        logger.exception(f'У компании не заполнен реквизит')
        full_name = company['TITLE']
    if req:
        if isinstance(req,list) and 'NAME' in req[0]:
            req=req[0]  #  !!!!!! осторожно , берется ПЕРВАЯ ЗАПИСЬ

        full_name = req['RQ_COMPANY_FULL_NAME']
    # Если не заполнен телефон или почта
    # Лепим заглушки
    if not "PHONE" in company.keys():
        phone = ''
        logger.exception(f'У компании нет телефона')
    elif "PHONE" in company.keys():
        phone = company['PHONE'][0]['VALUE']
    if not "EMAIL" in company.keys():
        email = ''
        logger.exception(f'У компании нет почты')
    elif "EMAIL" in company.keys():
        email = company['EMAIL'][0]['VALUE']
    try:
        company_1c = func_1c.company_add_or_get(
            inn=company['UF_CRM_1690987965649'],
            kpp=company['UF_CRM_1700522340677'],
            guid='00000000-0000-0000-0000-000000000000',
            create='1',
            id_bitrix=company['ID'],
            name=company['TITLE'],
            full_name=full_name,
            short_name=company['TITLE'],
            entity_type='entity',
            phone=phone,
            email=email,
        )
        company_1c_guid = company_1c['#value'][0]['#value']
        logger.info(f'Компания добавлена в 1С -> {company_1c_guid}')
        func.b.call('crm.company.update', {
            'id': company_id,
            'fields': {
                'UF_CRM_1700513351': company_1c_guid
            }
        })
        return {
            'company': company,
            'user_login': ad_login,
            'user_1c_guid': user_1c_guid,
            'company_1c_guid': company_1c_guid
        }
    except Exception as e:
        logger.exception(f'Не удалось добавить компанию в 1С -> {e}')


@app.post('/1c/company_check/')
def company_check(company_id):
    """ ## Метод для получения 1С ГУИД
        - Сохраняет в Б24 актуальный GUID"""

    # Инициализируем объект ответа
    response = {}

    # Получаем гуид из б24
    company = func.b.call('crm.company.get', {'id':company_id})
    guid_b24 = company['UF_CRM_1700513351']
    inn = company['UF_CRM_1690987965649']
    kpp = company['UF_CRM_1700522340677']
    response['b24_guid'] = guid_b24
    # Получаем гуид 1C
    guid_1c = func_1c.company_add_or_get(inn=inn, kpp=kpp, create='0')['#value'][0]['#value']
    response['1c_guid'] = guid_1c
    # Проверка ГУИД компании в б24
    # Если не не совпадает
    if guid_b24 != guid_1c:
        # Перезаписываем гуид б24 данными из 1с
        response['condition'] = f'Гуид в б24 не совпадает с гуидом из 1С'
        func.b.call('crm.company.update', {'id': company_id, 'fields': {'UF_CRM_1700513351': guid_1c}})
        response['action'] = f'Гуид в б24 обновлен данными из 1с {guid_b24} --> {guid_1c}'
        return response
    else:
        response['condition'] = f'Гуид в б24 совпадает с гуидом из 1С'
        response['action'] = f'Компания {company_id} уже привязана к 1С, доп действий не требуется'
        return response


@app.post('/1c/company_shipment_update/')
def company_shipment_update(company_id, shipment_state: bool):
    """# Разрешить или запретить в 1С


    """
    if shipment_state:
        shipment = 1
    if not shipment_state:
        shipment = 0
    logger.info('Получен запрос на изменение статуса отгрузки компании в 1С')
    logger.info(f'BX_ID = {company_id}, shipment_state = {shipment}')
    company = func.b.call('crm.company.get', {'id': company_id})
    print(company)
    company_guid = company['UF_CRM_1700513351']
    logger.info(f'BX_ID = {company_id}, shipment_state = {shipment}, 1C_GUID={company_guid}')

    shipment_state_before_upd = func_1c.check_1c_company_shipment_status(company_guid)
    logger.info(f'Статус отгрузки до изменений | СДЕЛКИ_ЗАПРЕЩЕНЫ={shipment_state_before_upd}')

    upd = func_1c.company_shipment_update(company_guid, shipment)
    logger.info(upd)

    shipment_state_after_upd = func_1c.check_1c_company_shipment_status(company_guid)
    logger.info(f'Статус отгрузки после изменений | СДЕЛКИ_ЗАПРЕЩЕНЫ={shipment_state_after_upd}')

    if shipment_state_before_upd != shipment_state_after_upd:
        upd_state = 'Компания успешно изменена'
    else:
        logger.critical('При изменении компании произошла ошибка')
        upd_state = 'При изменении компании произошла ошибка'
    return {
        'bx_id': company_id,
        'GUID': company_guid,
        'upd_state': upd_state,
        'shipment_state_before_upd': {"СДЕЛКИ_ЗАПРЕЩЕНЫ": shipment_state_before_upd},
        'shipment_state_after_upd': {"СДЕЛКИ_ЗАПРЕЩЕНЫ": shipment_state_after_upd},
    }


@app.post('/1c/user_guid_get/')
def user_guid_get(bx_user_id):
    """На вход принимает ID юзера в Битрикс24, на выходе отдает guid пользователя в 1С"""
    logger.info(f'Получен запрос на получение адешного логина пользователя по bx_id={bx_user_id}')
    user_domain_login = func.user_get_domain_login(bx_user_id)
    logger.info(f'Получен адэшный логин -> {user_domain_login}')
    user_1c_guid = func_1c.get_1c_user_guid(user_domain_login)
    logger.info(f'Получен 1C GUID логин -> {user_domain_login}')
    return {
        'user_bx_id': bx_user_id,
        'user_1c_guid': user_1c_guid,
        'user_domain_login': user_domain_login,
    }


@app.post('/1c/contract_add/')
def contract_add(contract_id):
    """# Создание договора в 1С

    Принимает ID договора в Б24 и создает соответствующий договор в 1С.

    ```
    Parameters:
        contract_id (str): ID договора в Б24.

    Returns:
        str: GUID созданного договора в 1С.
    ```

    Функция получает данные о договоре из Б24, включая данные о контрагенте, организации,
    и другие необходимые данные. Затем она преобразует даты начала и окончания договора
    в формат, подходящий для передачи в 1С. После создания договора в 1С, функция обновляет
    поле `ufCrm4_1708277405331` в Б24 с GUID нового договора и возвращает этот GUID.

    """

    logger.info(f'Получен запрос на создание договора, id карточки догра в б24 -> {contract_id}')
    logger.info('Получаю данные для формирования договора в 1С')

    contract = func.b.get_all('crm.item.get', {'entityTypeId': '162', 'id': contract_id})['item']
    company = func.b.call('crm.company.get', {'id': contract['companyId']})
    our_company = func.b.call('crm.company.get', {'id': contract['ufCrm4_1696252759']})

    company_guid = company['UF_CRM_1700513351']
    our_company_guid = our_company['UF_CRM_1700513351']
    user_1c_guid = user_guid_get(contract['assignedById'])['user_1c_guid']

    # Преобразование даты закрытия договора в нужный формат
    contract_close_date = datetime.strptime(contract['ufCrm4_1698835792'], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y%m%d")
    # Преобразование даты начала договора в нужный формат
    contract_start_date = datetime.strptime(contract['ufCrm4_1696252347618'], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y%m%d")

    contract = func_1c.contract_add(
        create='1',  # Создать
        guid='00000000-0000-0000-0000-000000000000',  # ГУИД Договора
        bitrix_id=contract_id,  # Bitrix id
        name=contract['title'],  # Наименование
        organization_guid=our_company_guid,  # ГУИД Организации
        counterparty_guid=company_guid,  # ГУИД Контрагента
        contract_type='Продажа',  # Вид Договора
        start_date=contract_start_date,  # Дата Начала
        end_date=contract_close_date,  # Дата Окончания
        auto_prolongation='0',  # Автопролонгация
        service='1',  # Сервис
        responsible_manager_guid=user_1c_guid,  # ГУИД Ответственного Менеджера
        prepayment_percentage=contract['ufCrm4_1696266371968'],  # Процент Предоплаты
        loan_amount=contract['ufCrm4_1696266393755'],  # Сумма Кредита
        payment_term=contract['ufCrm4_1697045531854'],  # Срок Оплаты
        comment=f'Договор создан автоматически из битрикс24, ссылка на договор -> https://orgtraid.ru/crm/type/162/details/{contract_id}/',
        # Комментарий
        contract_number=contract['ufCrm4_1696418663226'],  # Номер Договора
        currency='643'  # Валюта
    )
    contract_guid = contract['#value'][0]['Value']['#value']

    upd = func.b.call('crm.item.update', {
        "entityTypeId": 162,
        "id": int(contract_id),
        'fields': {
            'ufCrm4_1708277405331': contract_guid
        }}, raw=True)

    return contract_guid


@app.post('/1c/contract_get/')
def contract_get_shipment_status(contract_id):
    """
    Получение значение поля `Сделки запрещены` по договору в 1С
    """
    contract_guid = func.b.get_all('crm.item.get', {'entityTypeId': '162', 'id': contract_id})['item'][
        'ufCrm4_1708277405331']
    shipment_status = func_1c.check_1c_contract_shipment_status(contract_guid)
    return {
        'contract_id': contract_id,
        'contract_guid': contract_guid,
        'shipment_status': shipment_status
    }


@app.post('/1c/contract_update/')
def contract_update_shipment_status(contract_id, shipment_state: bool):
    """
    # Разрешить или запретить отгрузки для договора в 1С
    Принимает на вход `ID договора` в битриксе, изменяет значение поля `Сделки запрещены`
    """

    contract_guid = func.b.get_all('crm.item.get', {'entityTypeId': '162', 'id': contract_id})['item'][
        'ufCrm4_1708277405331']
    shipment_status_before_upd = func_1c.check_1c_contract_shipment_status(contract_guid)
    contract_update = func_1c.contract_upd(guid=contract_guid, shipment_state=shipment_state)
    shipment_status_after_upd = func_1c.check_1c_contract_shipment_status(contract_guid)

    return {
        'contract_id': contract_id,
        'contract_guid': contract_guid,
        'shipment_status_before_upd': shipment_status_before_upd,
        'shipment_status_after_upd': shipment_status_after_upd,
    }


