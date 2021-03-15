import requests
from bs4 import BeautifulSoup
import re
import argparse
import sys


class LanguageNotSupported(Exception):
    def __init__(self, value):
        self.message = f"Sorry, the program doesn't support {value}"
        super().__init__(self.message)


class Translator:
    languages = (
        'all',
        'arabic',
        'german',
        'english',
        'spanish',
        'french',
        'hebrew',
        'japanese',
        'dutch',
        'polish',
        'portuguese',
        'romanian',
        'russian',
        'turkish'
    )

    def __init__(self, src, trg, word):
        self.scr = src
        self.trg = trg
        self.word = word
        self.translations = None
        self.examples = None

    def get_content(self):
        direction = f"{self.scr}-{self.trg}"
        url = f"https://context.reverso.net/translation/{direction}/{self.word}"
        headers = {'user-agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return r.content
        except requests.exceptions.ConnectionError:
            print('Something wrong with your internet connection')
            sys.exit(1)

    def translate(self, n):
        content = self.get_content()
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            no_results = soup.find("section", {"id": "no-results"})
            translations_tags = soup.find_all(['div', 'a'], {"class": re.compile("translation.*dict")})
            self.translations = [t.text.strip() for t in translations_tags][:n]
            examples_src = soup.find_all("div", {"class": re.compile(r"^(src).((ltr)|(rtl))")})
            examples_trg = soup.find_all("div", {"class": re.compile(r"^(trg).((ltr)|(rtl))")})
            examples_result = zip([e.text.strip() for e in examples_src], [e.text.strip() for e in examples_trg])
            self.examples = [f'{example[0]}\n{example[1]}' for example in list(examples_result)[:n]]

    def result(self):
        if self.translations:
            translations = "\n".join(map(str, self.translations))
            examples = "\n\n".join(map(str, self.examples))
            return f'{self.trg.capitalize()} Translations:\n{translations}\n\n{self.trg.capitalize()} Examples:\n{examples}'
        else:
            print(f'Sorry, unable to find {self.word}')
            sys.exit(1)

    def __str__(self):
        return str(self.result())


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Multilingual online translator .")
        parser.add_argument("src")
        parser.add_argument("trg")
        parser.add_argument("word")
        args = parser.parse_args()
        if args.src not in Translator.languages:
            raise LanguageNotSupported(args.src)
        if args.trg not in Translator.languages:
            raise LanguageNotSupported(args.trg)
        if args.trg != 'all':
            word = Translator(args.src, args.trg, args.word)
            word.translate(5)
            print(word)
            with open(f'{args.word}.txt', 'w', encoding='utf-8') as file:
                file.write(str(word.result()))

        else:
            open(f'{args.word}.txt', 'w', ).close()
            with open(f'{args.word}.txt', 'a', encoding='utf-8') as file:
                for lang in Translator.languages[1:]:
                    if lang != args.src:
                        word = Translator(args.src, lang, args.word)
                        word.translate(1)
                        print(f'{word}\n')
                        file.write(f'{word.result()}\n\n')
    except Exception as e:
        print(e)
