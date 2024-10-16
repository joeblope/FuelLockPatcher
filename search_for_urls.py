import requests
import os
import bs4
from enum import StrEnum
import json


class ProxyHandler:

    def __init__(self, enable_http: bool = True, enable_socks4: bool = False, enable_socks5: bool = False):
        self.enable_http = enable_http
        self.enable_socks4 = enable_socks4
        self.enable_socks5 = enable_socks5

        self.update_proxy_list()


    def update_proxy_list(self):
        http_proxies_url = "https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/http.txt"
        socks4_proxies_url = "https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/socks4.txt"
        socks5_proxies_url = "https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/socks5.txt"

        if self.enable_http:
            response = requests.get(http_proxies_url)
            if response.status_code != 200:
                print("Failed to fetch HTTP proxies")
                print(response.status_code)
                print(response.text)
                assert response.status_code == 200, "Failed to fetch HTTP proxies"
            self.http_proxies = response.text.split("\n")
            print(f"HTTP Proxies: {len(self.http_proxies)}")

        if self.enable_socks4:
            response = requests.get(socks4_proxies_url)
            if response.status_code != 200:
                print("Failed to fetch SOCKS4 proxies")
                print(response.status_code)
                print(response.text)
                assert response.status_code == 200, "Failed to fetch SOCKS4 proxies"
            self.socks4_proxies = response.text.split("\n")
            print(f"SOCKS4 Proxies: {len(self.socks4_proxies)}")

        if self.enable_socks5:
            response = requests.get(socks5_proxies_url)
            if response.status_code != 200:
                print("Failed to fetch SOCKS5 proxies")
                print(response.status_code)
                print(response.text)
                assert response.status_code == 200, "Failed to fetch SOCKS5 proxies"
            self.socks5_proxies = response.text.split("\n")
            print(f"SOCKS5 Proxies: {len(self.socks5_proxies)}")

    def get_proxy(self, protocol: str):
        if protocol == "http" and self.enable_http:
            return self.http_proxies.pop()
        elif protocol == "socks4" and self.enable_socks4:
           return self.socks4_proxies.pop()
        elif protocol == "socks5" and self.enable_socks5:
           return self.socks5_proxies.pop()
        else:
            return None


proxies = ProxyHandler()


class APKCombo:
    class DPI(StrEnum):
        LDPI = "120"
        MDPI = "160"
        HDPI = "240"
        XHDPI = "320"
        XXHDPI = "480"
        XXXHDPI = "640"
        TVDPI = "213"

    class Architecture(StrEnum):
        ARMEABI_V7A = "armeabi-v7a"
        ARM64_V8A = "arm64-v8a"
        X86 = "x86"
        X86_64 = "x86_64"

    class Lang(StrEnum):
        EN = "en"
        AR = "ar"
        ES = "es"
        DE = "de"
        PT = "pt"
        FR = "fr"
        RU = "ru"
        HI = "hi"
        ID = "id"
        IT = "it"
        JA = "ja"
        KO = "ko"
        NL = "nl"
        VI = "vi"
        PL = "pl"
        TR = "tr"
        TH = "th"
        TW = "tw"
        ZH = "zh"

    @staticmethod
    def search(retries: int = 50):
        if retries <= 0:
            raise Exception("Failed to search for apks")
        url = f"https://apkcombo.com/my-7-eleven/au.com.fuel7eleven/download/apk"
        proxy = proxies.get_proxy("http")
        print(f"Searching with proxy {proxy}")
        response = requests.get(url, proxies={"http": proxy})
        # response = requests.get(url)
        if response.status_code != 200:
            print("Failed to fetch APKCombo search results")
            print(response.status_code)
            print(response.text)
            print(f"Retrying... {retries} left")
            return APKCombo.search(retries-1)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        apks = []
        # find all hrefs
        for a in soup.find_all("a", href=True):
            if "download.apkcombo.com" in a["href"]:
                apks.append(a["href"])
        # verify that only 7 eleven apks are returned
        apks = [apk for apk in apks if "au.com.fuel7eleven" in apk]
        if len(apks) == 0:
            print(f"No APKs found, retrying... {retries} left")
            return APKCombo.search(retries-1)
        return apks


if __name__ == "__main__":
    apks = APKCombo.search()
    #stupid
    if 'GITHUB_ENV' in os.environ:
        with open(os.environ['GITHUB_ENV'], 'a') as fh:
            print(f'apk_urls={json.dumps(apks)}', file=fh)

    print(json.dumps(apks))



