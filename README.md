# HanserDownloader

Script to collect and download all pdf files for a book on the Hanser Verlag website.
For example from this page: https://www.hanser-elibrary.com/isbn/9783446453968

Install uv: https://docs.astral.sh/uv/getting-started/installation/

Run python version with:
```bash
uv run python download_pdfs.py --dir "D:\\Downloads\\Hanser\\" --url "https://www.hanser-elibrary.com/isbn/9783446453968"
```

Run exe version with:
```bash
download_pdfs.exe
```
It will then prompt you for the directory and url.

Test with:
```bash
uv run coverage run -m pytest
uv run coverage report -m
uv run coverage html
```
