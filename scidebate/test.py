import requests
from bs4 import BeautifulSoup   
import json

def search_science_papers(keyword, max_results=2):
    query_url = f"http://export.arxiv.org/api/query?search_query=all:{keyword.replace(' ', '+')}&start=0&max_results={max_results}"

    print(f"Fetching papers for keyword: '{keyword}'...")

    try:
        response = requests.get(query_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('entry')
        papers_list = []

        for entry in entries:
            authors = [author.find("name").text for author in entry.find_all("author")]

            paper_info = {
                "title": entry.find("title").text.strip().replace("\n", " "),
                "authors": authors,
                "published": entry.find("published").text,
                "summary": entry.find("summary").text.strip().replace("\n", " ")[:50],
                "link": entry.find("id").text,
                "updated": entry.find("updated").text
            }

            papers_list.append(paper_info)
        
        final_json = json.dumps(papers_list, indent=4, ensure_ascii=False)
        return final_json
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=4)
    
if __name__ == "__main__":
    keyword = "machine learning"
    papers_json = search_science_papers(keyword)
    print(papers_json)