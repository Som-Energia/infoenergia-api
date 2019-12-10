import os
import time

import connexion
import six
from connexion.mock import MockResolver
from jose import JWTError, jwt
from werkzeug.exceptions import Unauthorized

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

JWT_ISSUER = 'som-energia'
JWT_SECRET = 'j4h5gf6d78RFJTHGYH(/&%$·sdgfh'
JWT_LIFETIME_SECONDS = 1600
JWT_ALGORITHM = 'HS256'

tokens = {}


def basic_auth(username, password):
    if username == 'admin' and password == 'secret':
        timestamp = _current_timestamp()
        payload = {
            "iss": JWT_ISSUER,
            "iat": int(timestamp),
            "exp": int(timestamp + JWT_LIFETIME_SECONDS),
            "sub": str(username),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        tokens[username] = token
        return token
    else:
        # optional: raise exception for custom error response
        return ('Invalid credentials', 401)


def _current_timestamp():
    return int(time.time())


def decode_token(token):
    try:
        if token in tokens.values():
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)


def get_contract_by_id(user, token_info, contractId):
    return {'contractId': contractId,
            'ownerId': 'ownerId-123',
            'payerId': 'payerId-123',
            'power': 23,
            'power_':
            {
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            },
            'powerHistory':
            [{
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            },
                {
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            }],
            'dateSart': '2019-10-22',
            'dateEnd': None,
            'tertiaryPower':
            {
                'p1': None,
                'p2': None,
                'p3': None
            },
            'climaticZone': 'climaticZone-2',
            'experimentalGroupUser': True,
            'experimentalGroupUserTest': True,
            'buildingData':
            {
                'buildingConstructionYear': 2014,
                'dwellingArea': 196,
                'propertyType': 'primary',
                'buildingType': 'Apartment',
                'dwellingPositionInBuilding': 'first_floor',
                'dwellingOrientation': 'SE',
                'buildingWindowsType': 'double_panel',
                'buildingWindowsFrame': 'PVC',
                'buildingCoolingSource': 'electricity',
                'buildingHeatingSource': 'district_heating',
                'buildingHeatingSourceDhw': 'gasoil',
                'buildingSolarSystem': 'not_installed'
            },
            'customer':
            {
                'customerId': 'customerId-123',
                'address':
                {
                    'buildingId': 'building-123',
                    'city': 'city-123',
                    'cityCode': 'cityCode-123',
                    'countryCode': 'ES',
                    'country': 'Spain',
                    'postalCode': 'postalCode-123',
                    'province': 'Barcelona',
                    'provinceCode': 'provinceCode-123',
                    'parcelNumber': 'parcelNumber-123',
                }
            },
            'profile':
            {
                'totalPersonsNumber': 3,
                'minorsPersonsNumber': 0,
                'workingAgePersonsNumber': 2,
                'retiredAgePersonsNumber': 1,
                'malePersonsNumber': 2,
                'femalePersonsNumber': 1,
                'educationLevel':
                {
                    'edu_prim': 0,
                    'edu_sec': 1,
                    'edu_uni': 1,
                    'edu_noStudies': 1
                }
            },
            'activityCode': 'activityCode - activityCodeDescription',
            'tariffId': 'tariffId-123',
            'customisedGroupingCriteria':
            {
                'criteria_1': 'CLASS 1',
                'criteria_2': 'XXXXXXX',
                'criteria_3': 'YYYYYYY'
            },
            'customisedServiceParameters':
            {
                'OT701': 'p1;p2;px'
            },
            'meteringPointId': 'c1759810-90f3',
            'devices':
            [{
                'dateStart': '2019-10-11T16:37:05Z',
                'dateEnd': None,
                'deviceId': 'c1810810-0381-012d-25a8-0017f2cd3574'
            }],
            'version': 1,
            'report':
            {
                'initialMonth': '201902',
                'language': 'ES'
            }
            }


def get_contracts(user, token_info, limit, from_, to_, tariff, juridic_type):

    ContractsList = [
        {
            'contractId': '1',
            'ownerId': 'ownerId-123',
            'payerId': 'ownerId-123',
            'power': 23,
            'power_':
            {
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            },
            'powerHistory':
            [{
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            },
                {
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            }],
            'dateSart': from_,
            'dateEnd': to_,
            'tertiaryPower':
            {
                'p1': None,
                'p2': None,
                'p3': None
            },
            'climaticZone': 'climaticZone-2',
            'experimentalGroupUser': True,
            'experimentalGroupUserTest': True,
            'buildingData':
            {
                'buildingConstructionYear': 2014,
                'dwellingArea': 196,
                'propertyType': 'primary',
                'buildingType': 'Apartment',
                'dwellingPositionInBuilding': 'first_floor',
                'dwellingOrientation': 'SE',
                'buildingWindowsType': 'double_panel',
                'buildingWindowsFrame': 'PVC',
                'buildingCoolingSource': 'electricity',
                'buildingHeatingSource': 'district_heating',
                'buildingHeatingSourceDhw': 'gasoil',
                'buildingSolarSystem': 'not_installed'
            },
            'customer':
            {
                'customerId': 'customerId-123',
                'address':
                {
                    'buildingId': 'building-123',
                    'city': 'city-123',
                    'cityCode': 'cityCode-123',
                    'countryCode': 'ES',
                    'country': 'Spain',
                    'postalCode': 'postalCode-123',
                    'province': 'Barcelona',
                    'provinceCode': 'provinceCode-123',
                    'parcelNumber': 'parcelNumber-123',
                }
            },
            'profile':
            {
                'totalPersonsNumber': 3,
                'minorsPersonsNumber': 0,
                'workingAgePersonsNumber': 2,
                'retiredAgePersonsNumber': 1,
                'malePersonsNumber': 2,
                'femalePersonsNumber': 1,
                'educationLevel':
                {
                    'edu_prim': 0,
                    'edu_sec': 1,
                    'edu_uni': 1,
                    'edu_noStudies': 1
                }
            },
            'activityCode': 'activityCode - activityCodeDescription',
            'tariffId': 'tariffId-123',
            'customisedGroupingCriteria':
            {
                'criteria_1': 'CLASS 1',
                'criteria_2': 'XXXXXXX',
                'criteria_3': 'YYYYYYY'
            },
            'customisedServiceParameters':
            {
                'OT701': 'p1;p2;px'
            },
            'meteringPointId': 'c1759810-90f3',
            'devices':
            [{
                'dateStart': '2019-10-11T16:37:05Z',
                'dateEnd': None,
                'deviceId': 'c1810810-0381-012d-25a8-0017f2cd3574'
            }],
            'version': 1,
            'report':
            {
                'initialMonth': '201902',
                'language': 'ES'
            }
        },
        {
            'contractId': '2',
            'ownerId': 'ownerId-123',
            'payerId': 'ownerId-123',
            'power': 23,
            'power_':
            {
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            },
            'powerHistory':
            [{
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            },
                {
                'power': 23,
                'dateStart': '2019-10-20',
                'dateEnd': '2019-10-21'
            }],
            'dateSart': from_,
            'dateEnd': '2019-10-22',
            'tertiaryPower':
            {
                'p1': None,
                'p2': None,
                'p3': None
            },
            'climaticZone': 'climaticZone-2',
            'experimentalGroupUser': True,
            'experimentalGroupUserTest': True,
            'buildingData':
            {
                'buildingConstructionYear': 2014,
                'dwellingArea': 196,
                'propertyType': 'primary',
                'buildingType': 'Apartment',
                'dwellingPositionInBuilding': 'first_floor',
                'dwellingOrientation': 'SE',
                'buildingWindowsType': 'double_panel',
                'buildingWindowsFrame': 'PVC',
                'buildingCoolingSource': 'electricity',
                'buildingHeatingSource': 'district_heating',
                'buildingHeatingSourceDhw': 'gasoil',
                'buildingSolarSystem': 'not_installed'
            },
            'customer':
            {
                'customerId': 'customerId-123',
                'address':
                {
                    'buildingId': 'building-123',
                    'city': 'city-123',
                    'cityCode': 'cityCode-123',
                    'countryCode': 'ES',
                    'country': 'Spain',
                    'postalCode': 'postalCode-123',
                    'province': 'Barcelona',
                    'provinceCode': 'provinceCode-123',
                    'parcelNumber': 'parcelNumber-123',
                }
            },
            'profile':
            {
                'totalPersonsNumber': 3,
                'minorsPersonsNumber': 0,
                'workingAgePersonsNumber': 2,
                'retiredAgePersonsNumber': 1,
                'malePersonsNumber': 2,
                'femalePersonsNumber': 1,
                'educationLevel':
                {
                    'edu_prim': 0,
                    'edu_sec': 1,
                    'edu_uni': 1,
                    'edu_noStudies': 1
                }
            },
            'activityCode': 'activityCode - activityCodeDescription',
            'tariffId': 'tariffId-123',
            'customisedGroupingCriteria':
            {
                'criteria_1': 'CLASS 1',
                'criteria_2': 'XXXXXXX',
                'criteria_3': 'YYYYYYY'
            },
            'customisedServiceParameters':
            {
                'OT701': 'p1;p2;px'
            },
            'meteringPointId': 'c1759810-90f3',
            'devices':
            [{
                'dateStart': '2019-10-11T16:37:05Z',
                'dateEnd': None,
                'deviceId': 'c1810810-0381-012d-25a8-0017f2cd3574'
            }],
            'version': 1,
            'report':
            {
                'initialMonth': '201902',
                'language': 'ES'
            }
        }
    ]
    return ContractsList[:limit]


if __name__ == '__main__':
    api_extra_args = {}
    resolver = MockResolver(mock_all=False)
    api_extra_args['resolver'] = resolver

    app = connexion.FlaskApp(
        __name__,
        specification_dir=os.path.join(BASE_DIR, 'docs/'),
        debug=True,
    )
    app.add_api(
        'infoenergia-api.yaml',
        validate_responses=True,
        **api_extra_args
    )

    app.run(host='localhost', port=8090)
