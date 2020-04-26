from typing import Dict, Tuple, Sequence
import requests
from requests.exceptions import HTTPError


from connectors.credential import Credential 
from .connector_interface import ConnectorInterface
from .cve_wrapper import CveWrapper


class Connector(ConnectorInterface):
    """
    http://cve-search.org/api/
    """
    def __init__(self, credentials):
        super().__init__(credentials)

    def search_by_cve_code(self, cve_code:str):
        url = f'{self.cve}{cve_code}'
        response = requests.get(url)
        cve_wrapper = CveWrapper(response.json())
        return cve_wrapper

    def get_last_30_cves(self):
        response = requests.get(self.last)
        return response

    def get_vendors_list(self):
        response = requests.get(self.vendor)
        return response

    def get_vendor_products(self, vendor:str):
        url = f'{self.vendor}{vendor}/'
        response = requests.get(url)
        return response

    def get_product(self, vendor:str, product:str):
        url = f'{self.vendor}{vendor}/{product}'
        response = requests.get(url)
        return response

    def get_db_info(self:str):
        response = requests.get(self.db_info)
        return response



if __name__ == "__main__":
    # \sarenka\backend>python connectors\cve_search\connector.py  
    credentials = Credential().cve_search
    connector = Connector(credentials)
    response = connector.search_by_cve_code("CVE-2010-3333")
    for p in response.products: 
        print(p)
    # print(connector.get_last_30_cves())
    # print(connector.get_vendors_list())
    # print(connector.get_vendor_products("microsoft"))
    # print(connector.get_product("microsoft","office"))
    # print(connector.get_db_info())
