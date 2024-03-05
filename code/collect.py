import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm

CONFERENCE = 'iclr'
YEAR = 2024

def collect_data_from_poster(paper_id):
    url = f"https://{CONFERENCE}.cc/virtual/{YEAR}/poster/{paper_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        script_text = script_tag.string.strip()
        script_data = json.loads(script_text)
        authors = (', ').join([author['name'] for author in script_data['author']])
        try:
            openreview = soup.find('a', {'title': 'OpenReview'})['href']
        except:
            openreview = url
    return authors, openreview


def collect_data_from_openreview():
    url = f"https://{CONFERENCE}.cc/virtual/{YEAR}/papers.html?filter=titles"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paper_info = []
    for link in tqdm(soup.find_all('a', href=True)):
        href = link['href']
        if f"/virtual/{YEAR}/poster/" in href:
            paper_title = link.text.strip()
            paper_id = int(href.split("/")[-1])
            authors, openreview = collect_data_from_poster(paper_id)
            paper_info.append((paper_id, paper_title, authors, openreview))
    df = pd.DataFrame(paper_info, columns=['paper_id', 'title',  'authors', 'openreview_link'])
    return df


def main():

    df = collect_data_from_openreview()
    df.to_csv('iclr2024.csv', index=False, columns=['title', 'openreview_link', 'authors'])


if __name__ == "__main__":
    main()
