import re
import time
import environ
import requests

env = environ.Env()

class Pipedrive():
    PIPEDRIVE_URL = 'https://api.pipedrive.com/v1'
    PIPEDRIVE_API_KEY = env.str('PIPEDRIVE_KEY')

    @classmethod
    def get_fields(cls) -> list:
        URL = f'{cls.PIPEDRIVE_URL}/leadFields'
        retry = 0
        data = None

        params = {
            'api_token': cls.PIPEDRIVE_API_KEY
        }

        while retry < 3:
            response = requests.get(url=URL, params=params)

            if response.ok:
                data = response.json()['data']
                break

            retry += 1
            time.sleep(2)

        return data

    @classmethod
    def get_person(cls, id) -> list:
        URL = f'{cls.PIPEDRIVE_URL}/persons/{id}'
        retry = 0
        data = None

        params = {
            'api_token': cls.PIPEDRIVE_API_KEY
        }

        while retry < 3:
            response = requests.get(url=URL, params=params)

            if response.ok:
                data = response.json()['data']
                break

            retry += 1
            time.sleep(2)

        return data

    @classmethod
    def get_field_by_key(cls, key: str, fields: list) -> dict:
        field = next(
            (field for field in fields if field['key'] == key),
            None
        )

        return field

    @classmethod
    def validate_contact(cls, raw_number: str) -> str:
        has_space = ' ' in raw_number

        if has_space:
            ddd, digits = raw_number.split()
            has_hyphen = '-' in digits

            if len(ddd) == 2:
                ddd = f"({ddd})"

            if not has_hyphen:
                if len(digits) == 9:
                    digits = f"{digits[:5]}-{digits[5:]}"
                elif len(digits) == 8:
                    digits = f"{digits[:4]}-{digits[4:]}"
                else:
                    raise ValueError('Invalid contact digits length')

            formatted_number = f"{ddd} {digits}"

            is_valid = re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', formatted_number)

            if is_valid:
                return formatted_number
            else:
                raise ValueError('Invalid contact in regex')

        else:
            raise ValueError('Invalid contact format')