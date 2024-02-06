from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai

def PI_Google_Scholar_research_articles_extraction(url_link, executable_path):
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("headless") 
    service = EdgeService(executable_path = executable_path)
    driver = webdriver.Edge(service = service, options = edge_options)

    driver.get(url_link)
    all_article_titles = []

    button = driver.find_element(By.ID, "gsc_a_ha")
    button.click()

    button1_locator = (By.ID, "gsc_bpf_more")
    timeout = 1

    while True:
        try:
            button1 = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(button1_locator)
            )
            button1.click()

        except Exception as e:
            break

    article_titles = driver.find_elements(By.CSS_SELECTOR, ".gsc_a_at")

    for title in article_titles:
        all_article_titles.append(str(title.text))

    return all_article_titles


def get_article_published_year(url_link, executable_path):
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("headless")
    service = EdgeService(executable_path = executable_path)
    driver = webdriver.Edge(service = service, options = edge_options)

    driver.get(url_link)
    all_published_years = []

    button = driver.find_element(By.ID, "gsc_a_ha")
    button.click()

    button1_locator = (By.ID, "gsc_bpf_more")
    timeout = 1

    while True:
        try:
            button1 = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(button1_locator)
            )
            button1.click()

        except Exception as e:
            break

    published_years = driver.find_elements(By.CSS_SELECTOR, ".gsc_a_h.gsc_a_hc.gs_ibl")
    for year in published_years:
        published_year = str(year.text)
        if published_year.isdigit():
            all_published_years.append(int(published_year))
    return all_published_years


def get_article_citations(url_link, executable_path):
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("headless")
    service = EdgeService(executable_path=executable_path)
    driver = webdriver.Edge(service=service, options=edge_options)

    driver.get(url_link)
    all_citations = []

    button = driver.find_element(By.ID, "gsc_a_ha")
    button.click()

    button1_locator = (By.ID, "gsc_bpf_more")
    timeout = 1

    while True:
        try:
            button1 = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(button1_locator)
            )
            button1.click()

        except Exception as e:
            break

    citations = driver.find_elements(By.CSS_SELECTOR, ".gsc_a_ac.gs_ibl")
    for citation in citations:
        citation_text = str(citation.text)
        # Convert citation values to integers, replace empty strings with 0
        all_citations.append(int(citation_text) if citation_text.isdigit() else 0)

    return all_citations


def get_article_urls(url_link, executable_path):
    edge_options = webdriver.EdgeOptions() 
    edge_options.add_argument("headless")
    service = EdgeService(executable_path = executable_path)
    driver = webdriver.Edge(service = service, options = edge_options)

    driver.get(url_link)
    all_article_urls = []

    button = driver.find_element(By.ID, "gsc_a_ha")
    button.click() 

    button1_locator = (By.ID, "gsc_bpf_more")
    timeout = 1 

    while True:
        try:
            button1 = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(button1_locator)
            )
            button1.click()
        
        except Exception as e:
            break 

    article_links = driver.find_elements(By.CLASS_NAME, "gsc_a_at")
    for link in article_links:
        url = link.get_attribute("href")
        all_article_urls.append(url)
    
    return all_article_urls


def get_author_names(url_link, executable_path):
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("headless")
    service = EdgeService(executable_path = executable_path)
    driver = webdriver.Edge(service = service, options = edge_options)

    driver.get(url_link)
    author_names = driver.find_elements(By.CLASS_NAME, "gsc_oci_value")
    texts = []
    for name in author_names:
        text = name.get_attribute("textContent")
        texts.append(text)
    print(texts)
    if len(texts) != 0:
        return texts[0]
    else:
        return []
    

def generate_chat_response1(prompt):

    chat = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )

    reply = chat.choices[0]["message"]["content"]
    print(f"ChatGPT: {reply}")