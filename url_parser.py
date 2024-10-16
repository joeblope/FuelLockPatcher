
import json
import argparse
import os

def try_parse(input_text: str) -> str:
    try:
        # Input is json list
        return json.dumps(json.loads(input_text))
    except ValueError:
        # Input must be a single url
        urls = input_text.split(' ')
        # Remove any 0 length urls
        urls = [url.strip() for url in urls if len(url)>0]
        return json.dumps(urls)
try_parse("http://example.com")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse a list of urls')
    parser.add_argument('--input', '-i', type=str, help='The input text', required=True)
    args = parser.parse_args()
    result = try_parse(args.input)
    # stupid
    if 'GITHUB_ENV' in os.environ:
        with open(os.environ['GITHUB_ENV'], 'a') as fh:
            print(f'apk_urls={result}', file=fh)
    print(result)