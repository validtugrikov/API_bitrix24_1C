import base64

WEBHOOK = 'https://orgtraid.ru/rest/1/ka2ys8p18shdylf92/'
DADATA_API_KEY = '58c75829a1akjh4kwhddf8f0fdc5e94b860dd4c8'
DADATA_API_SECRET = '41cf6bdee9a9skhejhksKJHGd405f3e90379803'
# Данные для авторизации в 1С
login = "Robot_Bitrix"
password = "RfhfylYhs65"
auth_string = f"{login}:{password}"
base64_auth_string = base64.b64encode(auth_string.encode()).decode()