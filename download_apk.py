import requests
import os
import bs4
from enum import StrEnum
from urllib.parse import unquote
import shutil
import argparse

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
    def search():

        url = f"https://apkcombo.com/my-7-eleven/au.com.fuel7eleven/download/apk"
        response = requests.get(url)
        assert response.status_code == 200, "Failed to fetch APKCombo search results"
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        apks = []
        #find all hrefs
        for a in soup.find_all("a", href=True):
            if "download.apkcombo.com" in a["href"]:
                apks.append(a["href"])
        return apks

    @staticmethod
    def download(url: str, out_dir: str):
        # Tokens are required to download anything from APKCombo
        token_url = "https://apkcombo.com/checkin"
        token_response = requests.post(token_url)
        if token_response.status_code != 200:
            print("Failed to fetch APKCombo download token")
            print(token_response.status_code)
            print(token_response.text)
            exit(1)
        token = token_response.text
        # Add token to the download links
        url = f"{url}&{token}"
        print(f"Successfully retrieved download token: {token}")
        print(f"New download URL: {url}")

        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to download APK!")
            print(response.status_code)
            print(response.text)
            exit(1)
        filename = url.split("/")[-1].split("?")[0].split("#")[0]
        # url decode
        filename = unquote(filename)
        # remove _apkcombo.com
        filename = filename.replace("_apkcombo.com", "")
        filename = filename.replace("apkcombo.com", "")
        filename = filename.replace("apkcombo", "")

        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, filename), "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Downloads an apk/xapk from a url')
    parser.add_argument('--url', '-y', type=str, help='URL of apk to download',
                        required=True)
    args = parser.parse_args()
    #apks = APKCombo.search()
    apks = [args.url]
    if os.path.exists("apks"):
        shutil.rmtree("apks")
    for apk in apks:
        APKCombo.download(apk, "apks")

    files = os.listdir("apks")

    if len(files) > 1:
        result = files
    elif len(files) == 1:
        result = files[0]
    else:
        result = ""
    print(result)
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'apk_file_name={result}', file=fh)
    # move the apk to the current directory
    for file in files:
        shutil.move(os.path.join("apks", file), file)


