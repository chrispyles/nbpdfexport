#!/usr/bin/env python3
"""
Generate PDF with cells with just given tag.

I can never figure out nbconvert's API, unfortunately.
"""
import argparse
import nbconvert
import nbformat
import tempfile
import asyncio
import tempfile
from pyppeteer import launch


async def html_to_pdf(html_file, pdf_file, timeout=30000):
    """
    Convert arbitrary HTML file to PDF
    """
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    # Waiting for networkidle0 seems to let mathjax render
    await page.goto(f'file:///{html_file}', {'waitUntil': ['networkidle0'], 'timeout': timeout})
    # Give it *some* margins to make it look a little prettier
    # I just made these up
    page_margins = {
        'left': '0.4in',
        'right': '0.4in',
        'top': '0.4in',
        'bottom': '0.4in'
    }
    await page.pdf({'path': pdf_file, 'margin': page_margins})
    await browser.close()


async def notebook_to_pdf(notebook_model, pdf_path, timeout=30000):
    """
    Convert given notebook model to PDF
    """
    exporter = nbconvert.HTMLExporter(config={})
    exported_html, _ = exporter.from_notebook_node(notebook_model)

    with tempfile.NamedTemporaryFile(suffix='.html') as f:
        f.write(exported_html.encode())
        f.flush()
        await html_to_pdf(f.name, pdf_path, timeout=timeout)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'notebook_path',
        help='Path to .ipynb file to convert'
    )
    argparser.add_argument(
        'pdf_path',
        help='Path to output PDF file to'
    )
    argparser.add_argument(
        '--timeout',
        nargs="?",
        default=30000,
        type=int,
        help="Default timeout for loading pages in pyppeteer"
    )

    args = argparser.parse_args()

    with open(args.notebook_path) as f:
        notebook_model = nbformat.read(f, as_version=4)
    asyncio.get_event_loop().run_until_complete(notebook_to_pdf(notebook_model, args.pdf_path, timeout=args.timeout))

if __name__ == '__main__':
    main()