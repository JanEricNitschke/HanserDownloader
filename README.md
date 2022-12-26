# HanserDownloader

Script to collect and download all pdf files for a book on the Hanser Verlag website.
For example from this page: https://www.hanser-elibrary.com/isbn/9783446453968

Install dependencies with:
```bash
pip install -r requirements.txt
```

Run with:
```bash
python download_pdfs.py --dir "D:\\Downloads\\Hanser\\" --url "https://www.hanser-elibrary.com/isbn/9783446453968"
```

Test with:
```bash
coverage run -m pytest
coverage report -m
coverage html
```