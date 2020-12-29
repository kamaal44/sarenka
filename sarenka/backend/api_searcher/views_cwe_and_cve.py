from connectors.credential import Credential, CredentialsNotFoundError
from connectors.cve_search.connector import Connector as CVEConnector
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .cve_and_cwe.cve_details_all import CVEDetailsAll
from .cve_and_cwe.cwe_all import CWEAll
from .cve_and_cwe.cwe_details_all import CWEDetailsAll
from .cve_and_cwe.mitre_cwe_scrapers import CWETableTop25Scraper, CWEDataScraper
from .cve_and_cwe.nist_cve_scrapers import NISTCVEScraper
from .cwe_crud import CWECRUD
from .views_common import Common
from .views_search_engines import logger


class CVESearchView(views.APIView):
    """Widok Django zwracajacy szczegółowe informacje o jednej podatności Common Vulnerabilities and Exposures (CVE)."""
    def get(self, request, cve_id):
        """
        Metoda zwracająca szczegółowe infromacje o konkretnej podatności po podaniu identyfikatora CVE

        """
        print("CVESearchView")
        logger.debug("Logger at CVESearchView test message")
        logger.warning("Logger at CVESearchView test message")
        logger.info("Logger at CVESearchView test message")
        logger.error("Logger at CVESearchView test message")
        try:
            server_address = Common(request).host_address
            nist_cve_scraper = NISTCVEScraper(cve_id, server_address)
            return Response(nist_cve_scraper.get_data())
        except AttributeError as ex:
            return Response({cve_id: "Unable to get information - probably this CVE doesn't exists."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"error": f"Unable to get information about CVE={cve_id}", "details": str(ex)},
                            status=status.HTTP_404_NOT_FOUND)


class CWETop25(APIView):
    """Widok Django zwracający informacje o TOP 25 najgroźniejszych słabościach oprogramowania."""
    def get(self, request):
        """
        Metoda zwracająca dane o 25 najpopularniejszych słabościach oprogramowania na podstawie żądania GET HTTP.
        Dane pochodzą ze strony https://cwe.mitre.org/top25/archive/2020/2020_cwe_top25.html
        :tags: CWE
        :param request: obiekt request dla widoku Django
        :return: dane w postaci json zawierajace ingormacje o hoście
        """
        try:
            server_address = Common(request).host_address
            return Response({"response": CWETableTop25Scraper(server_address).get_top_25()})
        except Exception as ex:
            return Response({"error": "Unable to get TOP 25 CWE from https://cwe.mitre.org/top25/archive/2020/2020_cwe_top25.html",
                             "details": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class CWEData(APIView):
    """
    Widok Django zwracajacy infromacje o Common Weakness Enumeration na podstawie podanego numeru CWE ID.
    :tags: CWE
    """
    def get(self, request, id_cwe:str):
        """
        Metoda zwracająca dane o słabości oprogramowania na podstawie identyfikatora CWE podanego przez użytkownika
        w zapytaniu GET HTTP.
        :tags: CWE
        :param request: obiekt request dla widoku Django
        :param id_cwe: kod identyfikujący słabość oprogramowania
        :return: json z danymi wybranej słabości oprogramowania
        """
        try:
            server_address = Common(request).host_address
            return Response(CWEDataScraper(id_cwe, server_address).get_data())
        except AttributeError:
            return Response({"message": f"Unable to get information about CWE={id_cwe}.",
                             "details": f" Please check if CWE with id={id_cwe} exists on https://cwe.mitre.org/."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"error": f"Unable to get data.",
                             "details": str(ex)},
                            status=status.HTTP_404_NOT_FOUND)


class CWEAllView(views.APIView):
    """Widok Django zwracający wszystkie kody CWE z podstawowywmi danymi takimi jak datę pobrania danych, źródło danych,
    identyfikator slabości, opis słabości, url do serwisu https://cwe.mitre.org ze szczegółowymi danymi,
    url do aplikacji SARENKA z najważniejszymi informacjami o konkretnej słabości."""

    def get(self, request):
        """
        Metoda zwracajaca podstawowe dane o wszystkich słabościach CWE z oficjalnego serwisu https://cwe.mitre.org.
        :param request: obiekt dla widoku Django z informacjami od użytkownika
        :return: podstawowe dane w formacie json o wszystkich słabościach CWE zawartych w feedach
        """
        try:
            server_address = Common(request).host_address
            response = CWEAll().render_output(server_address)
            return Response(response)
        except Exception as ex:
            Response({"error": "Unable to get all Common Weakness Enumeration data. "
                               "Please check is file sarenka/feedes/cwe_ids/cwe_all.json exists",
                      "details": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class CVEDetailsAllView(views.APIView):
    """Widok Django zwracającyh szczegółowe dane o wszystkich podatnościach
    Common Vulnerabilities and Exposures (CVE) pobranych z serwisu https://nvd.nist.gov/ """

    def get(self, request, page):
        """Metoda zwracajaca szczegółowe informacje o podantościach CVE z stronnicowaniem.
        Partia danych zwrócona jest na podstawie danych z żadania GET HTTP użytkownika"""
        try:
            if isinstance(page, int):
                server_address = Common(request).host_address
                response = CVEDetailsAll(page).render_output(server_address) #render_output(server_address)
                return Response(response)
            return Response({"message": "Unsupported type of user input data."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"error": "Unable to get CVE details data - check is files "
                                      "in folder sarenka\feedes\cve_details exist",
                             "details": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class CWEDetailsAllView(views.APIView):
    """Widok Django zwracajacy wszystkie słabości Common Weakness Enumeration ze szczegółowymi danymi.
    Wszystki identyfikatory CWE pochodza z https://cwe.mitre.org/data/published/cwe_latest.pdf"""

    def get(self, request, page):
        try:
            if isinstance(page, int):
                server_address = Common(request).host_address
                response = CWEDetailsAll(page).render_output(server_address)  # render_output(server_address)
                return Response(response)
            return Response({"message": "Unsupported type of user input data."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"error": "Unable to get all CWE details data - check is files "
                                      "in folder sarenka\feedes\cwe_details",
                             "details": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class AddCWEandCVE(views.APIView):
    def get(self, request):
        # nist_cve_scraper = NISTCVEScraper("CVE-2013-3621") CWE_NONE
        nist_cve_scraper = NISTCVEScraper("CVE-2019-4570")
        cve = nist_cve_scraper.get_data()

        cwe = cve["cwe"]

        # zapisz do bazy obiekt CWE
        cwe_crud = CWECRUD(cwe)
        cwe_crud.add()
        cwe_db_obj = cwe_crud.get()

        return Response({"message": "Żyjemy",
                         "cve": cve,
                         "cwe": cwe,
                         # "cwe_response": CWEModelSerializer(instance=cwe_db_obj).data,
                         "cwe_response": cwe_db_obj,
                         })


class ListVendors(views.APIView):
    """Widok Django zwracający dostawców oprogramowania z wykrytymi podatnościami CVE"""

    def get(self, request):
        """
        Metoda zwracajace dostawców dla których wykryto podatności Common Vulnerabilities and Exposures (CVE)
        na podstawie zapytania GET HTTP użytkownika. Wymaga uzupełnionych danych la serwisów trzecich.
        :tags: CVE
        :param request: obiekt dla widoku Django z informacjami od użytkownika
        :return: dane w postaci json zawierajace ingormacje o dostawcach dla których istnieją podntości CVE
        """
        try:
            credentials = Credential().cve_search
            connector = CVEConnector(credentials)
            vendors = connector.get_vendors_list()
            return Response(vendors)
        except CredentialsNotFoundError:
            host_address = Common(request).host_address
            settings_url = host_address + reverse('settings')
            return Response({"error": "Unable to get vendor list.",
                             "details":  f"Please check settings on {settings_url}"},
                                status=status.HTTP_400_BAD_REQUEST)
        except BaseException as ex:
            return Response({"error": "Unable to get vendor list.",
                             "details": str(ex)}, status=status.HTTP_400_BAD_REQUEST)