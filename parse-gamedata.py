import re
import json
import os
import unicodedata
import shutil
import time

def slugify(text, separator='-'):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s_]+', separator, text)

def main():
    pass

if __name__ == '__main__':
    main()