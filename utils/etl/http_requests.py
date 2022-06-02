import requests
import json
import pandas as pd


def get_response(arg, base_url='https://api-prod.footballindex.co.uk/'):
    """
    :param arg: additional params to pass
    :param base_url: url of the API to call
    :return: dict, response
    """

    request_url = base_url + arg

    return json.loads(requests.get(request_url).text)


def get_dataframe(arg, base_url='https://api-prod.footballindex.co.uk/', unpack='items'):
    """
    :param arg: additional params to pass
    :param base_url: url of the API to call
    :param unpack: unpack data stored in 'items'
    :return: pandas dataframe
    """

    response = get_response(arg, base_url=base_url)

    if unpack:
        response = response[unpack]

    return pd.DataFrame(response)
