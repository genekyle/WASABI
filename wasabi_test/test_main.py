from playwright.sync_api import sync_playwright
import os

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    
    # Navigate to the webpage
    url = 'https://careers.mta.org/jobs/14175824-specialist-software-engineer-microsoft-power-apps-slash-dynamics-365'
    page.goto(url)
    

    # Define base directory for saving data
    base_dir = 'training_data'
    os.makedirs(base_dir, exist_ok=True)

    # Save HTML content
    html_content = page.content()
    with open(os.path.join(base_dir, 'page.html'), 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Save CSS content
    css_links = page.eval_on_selector_all('link[rel="stylesheet"]', 'elements => elements.map(e => e.href)')
    css_contents = []
    for index, url in enumerate(css_links):
        if url:
            css_response = page.request.get(url)
            css_path = os.path.join(base_dir, f'style_{index}.css')
            with open(css_path, 'w', encoding='utf-8') as file:
                file.write(css_response.text())
            css_contents.append(css_path)

    # Save JavaScript content
    js_links = page.eval_on_selector_all('script[src]', 'elements => elements.map(e => e.src)')
    js_contents = []
    for index, url in enumerate(js_links):
        if url:
            js_response = page.request.get(url)
            js_path = os.path.join(base_dir, f'script_{index}.js')
            with open(js_path, 'w', encoding='utf-8') as file:
                file.write(js_response.text())
            js_contents.append(js_path)

    # Save notes
    notes_content = "This folder contains the captured HTML, CSS, and JavaScript from " + url
    with open(os.path.join(base_dir, 'notes.txt'), 'w', encoding='utf-8') as file:
        file.write(notes_content)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)