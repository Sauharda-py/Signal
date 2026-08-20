#Create 2 tools - web_search() , scrap_url() tool
from langchain.tools import tool
import requests # since we will be scraping
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
import os #file management
from rich import print # better printing

#load the env files
load_dotenv()

#tavily stuff
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query:str) -> str: #accepts a string and returns a string
    """
    This tool searches the web for reliable information on a particular topic. It accepts a string and returns a string , its return includes titles, URLs , and snippets.
    """#docstring
    #print("---------------WEB SEARCH TOOL USED----------------------")
    search_results = tavily.search(query=query,max_results=5)
    search_output = []
    for i in search_results['results']:
        search_output.append(
            f"Title: {i['title']}\nURL: {i['url']}\nSnippet: {i['content'][:300]}" #we are going to extract only 300 characters from the content because we are going to go into the url using scrap_url() either wise
        )

    return "\n---------------\n".join(search_output)

#print(web_search.invoke("Current info regarding iran usa war"))

@tool
def scrap_url(url:str) -> str:
    """
    This tool scrapes and returns clean text from the url supplied to it , for obtaining further information
    """
    #print("-------SCRAP TOOL USED -----------------")
    try:
        response = requests.get(url,timeout=8,headers={"User-agent": "Mozilla/5.0"})#tricks the website into thinking its a real user
        soup = BeautifulSoup(response.text,"html.parser")
        for i in soup(["script","style","nav","footer"]):# we dont need these
            i.decompose()
        return soup.get_text(separator=" ",strip=True)[:3000] #get only 3000 characters from the scrapped url
    except Exception as e:
        return f"Couldn't scrap url {str(e)}"

#print(scrap_url.invoke("https://en.wikipedia.org/wiki/AC_Milan"))