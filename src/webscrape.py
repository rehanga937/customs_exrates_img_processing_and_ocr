from playwright.sync_api import sync_playwright
import requests
import io

def collect_links(check_older_pages: bool = True) -> list[tuple[str,str]]:
    """Collects links from the customs website.

    Args:
        check_older_pages (bool, optional): If True, checks all the pages of the dynamic table for links. Defaults to True.

    Returns:
        list[tuple[str,str]]: list of collected links (each item is a tuple - (link name, link href))
    """
    all_links = []
    

    with sync_playwright() as p:
        
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.customs.gov.lk/exchange-rates/")
        # print(page.title())
        # page.screenshot(path="1.png")
        # page.wait_for_timeout(10000)

        # find the dynamic table next button
        next_button = page.locator('#supsystic-table-5_next')
        next_button_enabled = True

        while next_button_enabled:
            # check if the next button is enabled, or if the check_older_pages flag is False
            if next_button.get_attribute('class') == 'paginate_button next disabled': next_button_enabled = False
            if not check_older_pages: next_button_enabled = False
            
            # go to the dynamic table we are interested in
            table = page.locator('#supsystic-table-5')

            # collect the links currently visible in the dynamic table
            table_links = table.locator('a').all()
            for link in table_links:
                link_label = link.inner_html()
                link_href = link.get_attribute('href')
                if 'http' not in link_href: # actually had to add this cuz some links didn't have it
                    link_href = 'https://www.customs.gov.lk' + link_href
                all_links.append((link_label,link_href))

            if next_button_enabled: next_button.click()
        
        browser.close()

    return all_links

def download_pdf_as_bytesio(pdf_url: str) -> io.BytesIO:
    """Downloads a PDF from the given URL to BytesIO

    Args:
        pdf_url (str): URL

    Returns:
        io.BytesIO: Downloaded PDF
    """
    response = requests.get(pdf_url)
    pdf_bytes = io.BytesIO(response.content)
    return pdf_bytes
