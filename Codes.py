from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai 
import re 
import requests 
import os 
from pypdf import PdfReader 
from tqdm import tqdm 
import pandas as pd 
import numpy as np

# executable path is directory path to Microsoft Edge driver

# returns article titles, publication years, number of citations, links to works listed on a 
# member's Google Scholar profile
def PI_Google_Scholar_profiles(url_links, executable_path):
    edge_options = webdriver.EdgeOptions() 
    edge_options.add_argument("headless")
    service = EdgeService(executable_path = executable_path)
    driver = webdriver.Edge(service = service, options = edge_options)

    all_article_titles = []
    all_published_years = [] 
    all_citations = []
    all_article_urls = []

    for url_link in tqdm(url_links):
        articles = []
        years = []
        PI_citations = []
        article_urls = []

        driver.get(url_link)
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
            articles.append(str(title.text))
        all_article_titles.append(articles)

        published_years = driver.find_elements(By.CSS_SELECTOR, ".gsc_a_h.gsc_a_hc.gs_ibl")
        for year in published_years:
            published_year = str(year.text)
            if published_year.isdigit(): 
                years.append(int(published_year))
            else:
                years.append("No date")
        all_published_years.append(years)

        citations = driver.find_elements(By.CSS_SELECTOR, ".gsc_a_ac.gs_ibl")
        for citation in citations:
            citation_text = str(citation.text)
            PI_citations.append(int(citation_text) if citation_text.isdigit() else 0)
        all_citations.append(PI_citations)

        article_links = driver.find_elements(By.CLASS_NAME, "gsc_a_at")
        for link in article_links:
            url = link.get_attribute("href")
            article_urls.append(url)
        all_article_urls.append(article_urls)
    
    return all_article_titles, all_published_years, all_citations, all_article_urls

# clicks link to a member's work and obtains names of authors, journal name, abstract, and
# external links to paper
def google_scholar_author_names_journal_names_abstracts_pdf_links(url_links, executable_path):
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("headless")
    service = EdgeService(executable_path = executable_path)
    driver = webdriver.Edge(service = service, options = edge_options)

    driver.get("https://scholar.google.ca/scholar_settings?sciifh=1&hl=en&as_sdt=0,5#2")
    button = driver.find_element(By.CLASS_NAME, "gs_btn_act.gs_btn_lsb")
    button.click()

    all_author_names = []
    all_journal_names = []
    all_abstracts = []
    all_pdf_links = []

    for url_link in tqdm(url_links):
        driver.get(url_link)

        try:
            div_element = driver.find_element(By.XPATH, "//div[@class='gsc_oci_field' and text()='Authors']")
            authors_element = div_element.find_element(By.XPATH, "following-sibling::div[@class='gsc_oci_value']")
            all_author_names.append(authors_element.text)
        except Exception as e:
            all_author_names.append([])

        try:
            div_element = driver.find_element(By.XPATH, "//div[@class='gsc_oci_field' and text()='Journal']")
            journal_element = div_element.find_element(By.XPATH, "following-sibling::div[@class='gsc_oci_value']")
            all_journal_names.append(journal_element.text)
        except Exception as e:
            all_journal_names.append([])

        try:
            div_element = driver.find_element(By.XPATH, "//div[@class='gsc_oci_field' and text()='Description']")
            abstract_element = div_element.find_element(By.XPATH, "following-sibling::div[@class='gsc_oci_value']")
            all_abstracts.append(abstract_element.text)
        except Exception as e:
            all_abstracts.append([])

        pdf_links = driver.find_elements(By.CSS_SELECTOR, ".gsc_oci_title_ggi [href]")
        if len(pdf_links) != 0:
            pdf = pdf_links[0].get_attribute("href")
            # if "pdf" in pdf:
            #     all_pdf_links.append(pdf)
            all_pdf_links.append(pdf)
        else:
            all_pdf_links.append("No pdf link")
    
    return all_author_names, all_journal_names, all_abstracts, all_pdf_links

# given external link to a paper, this checks if pdf can be "easily" downloaded. If so, it is 
# saved by the article title in directory, which can be specified by member name, folder name
def download_pdfs(all_pdf_links, all_article_titles, member_names, folder_name, executable_path):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for article_titles, pdf_links, member_name in tqdm(zip(all_article_titles, all_pdf_links, member_names)):
        directory_path = folder_name + "\\" + member_name

        for article_title, pdf_link in zip(article_titles, pdf_links):
            if "pdf" in pdf_link and "No pdf link" not in pdf_link:
                try:
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)
                    article_title = article_title.replace(" ", "_")
                    article_title = re.sub(r"[^a-zA-Z]", "_", article_title)
                    file_path = os.path.join(directory_path, article_title + ".pdf")
                    response = requests.get(pdf_link)
                    with open(file_path, "wb") as file:
                        file.write(response.content)

                except Exception as e:
                    continue

            elif "pdf" not in pdf_link and "No pdf link" not in pdf_link:
                try:
                    edge_options = webdriver.EdgeOptions()
                    edge_options.add_argument("headless")
                    edge_options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.2151.97')
                    service = EdgeService(executable_path = executable_path)
                    driver = webdriver.Edge(service = service, options = edge_options)
                    
                    driver.get(pdf_link)
                    pdfs = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    pdf_urls = [link.get_attribute("href") for link in pdfs]
                    pdf_urls = list(set(pdf_urls))

                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)
                    article_title = article_title.replace(" ", "_")
                    article_title = re.sub(r"[^a-zA-Z]", "_", article_title)
                    
                    for i in range(len(pdf_urls)):
                        file_path = os.path.join(directory_path, article_title + "_" + str(i) + ".pdf")
                        response = requests.get(pdf_urls[i])
                        with open(file_path, "wb") as file:
                            file.write(response.content)

                except Exception as e:
                    continue

# simple text search to see if paper acknowledges funding by Acceleration Consortium and CFREF
def pdf_funding_reading(file_paths):
    AC_funding = []

    for file in tqdm(file_paths):
        count = 0
        try:
            reader = PdfReader(file)
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                extracted_text = page.extract_text().lower()
                if "acceleration" in extracted_text and "consortium" in extracted_text:
                    count += 1
                if "canada first research excellence fund" in extracted_text:
                    count += 1

        except Exception as e:
            continue 

        if count != 0:
            AC_funding.append("This work was funded by the Acceleration Consortium")
        else:
            AC_funding.append("This work was not funded by the Acceleration Consortium")
    
    return AC_funding

# ChatGPT API
def generate_chat_response1(prompt):

    chat = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )

    reply = chat.choices[0]["message"]["content"]
    print(f"ChatGPT: {reply}")



# Example usage
AC_members = pd.read_csv("Acceleration_Consortium_Members.csv")
AC_members_without_google_scholar_profiles_indices = AC_members[AC_members["Google Scholar profile"].isna()].index.to_list()
AC_members_with_google_scholar_profiles = AC_members.drop(AC_members_without_google_scholar_profiles_indices).reset_index(drop = True)

all_article_titles, all_published_years, all_citations, all_article_urls = PI_Google_Scholar_profiles(
    AC_members_with_google_scholar_profiles["Google Scholar profile"].values[:2], 
    "msedgedriver.exe"
)

all_author_names, all_journal_names, all_abstracts, all_pdf_links = google_scholar_author_names_journal_names_abstracts_pdf_links(
    all_article_urls[0][:10], 
    "msedgedriver.exe"
)
