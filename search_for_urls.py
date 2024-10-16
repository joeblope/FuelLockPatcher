import requests
import os
import bs4
from enum import StrEnum
import json
import concurrent.futures

class ProxyHandler:

    def __init__(self, enable_http: bool = True, enable_https: bool = True, enable_socks4: bool = True, enable_socks5: bool = True):
        self.enable_http = enable_http
        self.enable_https = enable_https
        self.enable_socks4 = enable_socks4
        self.enable_socks5 = enable_socks5

        self.update_proxy_list()


    def update_proxy_list(self):
        http_proxies_url = "https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/http.txt"
        socks4_proxies_url = "https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/socks4.txt"
        socks5_proxies_url = "https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/socks5.txt"

        #http_proxies_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
        #socks4_proxies_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"
        #socks5_proxies_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"

        #http_proxies_url = "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt"
        https_proxies_url = "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt"
        #socks4_proxies_url = "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt"
        #socks5_proxies_url = "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt"

        if self.enable_http:
            response = requests.get(http_proxies_url)
            if response.status_code != 200:
                print("Failed to fetch HTTP proxies")
                print(response.status_code)
                print(response.text)
                assert response.status_code == 200, "Failed to fetch HTTP proxies"
            self.http_proxies = response.text.split("\n")
            print(f"HTTP Proxies: {len(self.http_proxies)}")

        if self.enable_https:
            response = requests.get(https_proxies_url)
            if response.status_code != 200:
                print("Failed to fetch HTTPS proxies")
                print(response.status_code)
                print(response.text)
                assert response.status_code == 200, "Failed to fetch HTTPS proxies"
            self.https_proxies = response.text.split("\n")
            print(f"HTTPS Proxies: {len(self.https_proxies)}")

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

        if protocol == "http" and self.enable_http and len(self.http_proxies) > 0:
            proxy = self.http_proxies.pop()
            while proxy == "" and len(self.http_proxies) > 0:
                proxy = self.http_proxies.pop()
            return proxy
        elif protocol == "https" and self.enable_https and len(self.https_proxies) > 0:
            proxy = self.https_proxies.pop()
            while proxy == "" and len(self.https_proxies) > 0:
                proxy = self.https_proxies.pop()
            return proxy
        elif protocol == "socks4" and self.enable_socks4 and len(self.socks4_proxies) > 0:
            proxy = self.socks4_proxies.pop()
            while proxy == "" and len(self.socks4_proxies) > 0:
                proxy = self.socks4_proxies.pop()
            return proxy
        elif protocol == "socks5" and self.enable_socks5 and len(self.socks5_proxies) > 0:
            proxy = self.socks5_proxies.pop()
            while proxy == "" and len(self.socks5_proxies) > 0:
                proxy = self.socks5_proxies.pop()
            return proxy
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
    def fetch_with_proxy(proxy_type: str, proxy: str, url: str):
        selected_proxies = {
            "http": f"{proxy_type}://{proxy}",
            "https": f"{proxy_type}://{proxy}"
        }

        try:
            response = requests.get(url, proxies=selected_proxies, timeout=5)
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                apks = []
                # find all hrefs
                for a in soup.find_all("a", href=True):
                    if "download.apkcombo.com" in a["href"]:
                        apks.append(a["href"])
                # verify that only 7 eleven apks are returned
                apks = [apk for apk in apks if "au.com.fuel7eleven" in apk]
                if apks:
                    print(f"Found APKs with proxy {proxy}: {apks}")
                    return apks
            print(f"Failed with proxy {proxy}, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error with proxy {proxy}: {e}")
        return None

    @staticmethod
    def search_concurrently(proxies_list, url: str, max_workers: int = 20):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(APKCombo.fetch_with_proxy, proxy_type, proxy, url): proxy
                for proxy_type, proxy in proxies_list
            }
            for future in concurrent.futures.as_completed(future_to_proxy):
                result = future.result()
                if result:
                    # kill all other threads
                    for f in future_to_proxy:
                        f.cancel()
                    executor.shutdown(wait=False, cancel_futures=True)

                    return result
        raise Exception("Unable to search APK Combo")

    @staticmethod
    def search():
        proxies_list=[]
        while len(proxies.http_proxies) > 0 or len(proxies.https_proxies) > 0 or len(proxies.socks4_proxies) > 0 or len(proxies.socks5_proxies) > 0:
            http_proxy = proxies.get_proxy("http")
            if http_proxy:
                proxies_list.append(("http", http_proxy))
            https_proxy = proxies.get_proxy("https")
            if https_proxy:
                proxies_list.append(("https", https_proxy))
            socks4_proxy = proxies.get_proxy("socks4")
            if socks4_proxy:
                proxies_list.append(("socks4", socks4_proxy))
            socks5_proxy = proxies.get_proxy("socks5")
            if socks5_proxy:
                proxies_list.append(("socks5", socks5_proxy))
        return APKCombo.search_concurrently(proxies_list, "https://apkcombo.com/my-7-eleven/au.com.fuel7eleven/download/apk")



if __name__ == "__main__":
    apks = APKCombo.search()
    #stupid
    if 'GITHUB_ENV' in os.environ:
        with open(os.environ['GITHUB_ENV'], 'a') as fh:
            print(f'apk_urls={json.dumps(apks)}', file=fh)

    print(json.dumps(apks))



