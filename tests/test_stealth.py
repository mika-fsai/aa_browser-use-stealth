from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from urllib.parse import unquote, urlsplit
import aiohttp
from aiofiles import open as aio_open
import os
import asyncio
from browser_use import Agent, Browser
from playwright.async_api import async_playwright

load_dotenv()

def return_task(company_name):
    task = """
    ### Prompt for returning the link to a PDF file

    **Objective:**
    Visit [Google](https://www.google.com/search?complete=0&gbv=1), search for company "{0}". Navigate search results and find the most recent annual report or proxy statement PDF. return the URL for accessing this PDF file.

    **Important:**
    - Make sure that you return the PDF link asked for.
    - Make sure that you analyse all search results and find the most recent annual report or proxy statement PDF, including the first search result.
    - Do not click on the microphone icon, camera icon or any other icons and buttons within Google other than "Google Search" once you have entered the search query.
    - Make sure that the result is from a credible source such as the company's official website or a reputable financial website.
    - Prioritise results from the company's official website in sections such as Investor Relations or Financial Information.
    ---

    ### Step 1: Navigate to the Website
    - Open [Google](https://www.google.com/search?complete=0&gbv=1).
    - Search for the company name "{0}" and include keywords to help find relevant PDFs such as "annual report" and current year.
    - If suggestions appear, ignore them. They may cover the "Google Search" button, so make sure to click on the "Google Search" button.
    - Do not click on any other buttons or icons unless it contains the words "Google Search".
    - Click on "Google Search".
    - Wait for the search results to load.
    - Navigate to the most relevant search result involving the company, annual report, or proxy statement for the most recent year (2025).
    - The link must contain the words "annual report" or "proxy statement", or "investor relations".
    - Click on the link to open the page.
    - If you are unable to find a relevant link, refine your search query and repeat the process (such as using year 2024 instead of 2025).
    - If you are still unable to find a relevant link, return "No relevant link found".
    - If you are presented with a popup asking to enable cookies, click on Accept All.
    ---

    ### Step 2: Find relevant annual report or proxy statement
    - Locate the most recent annual report or proxy statement, for example "Annual Report 2025" or "Proxy Statement 2025" or "Digital Annual Report" or similar.
    - Before you click on any PDF, make sure that you are in the right section of the page such as Financial Information.
    - Make sure the PDF is either an annual report or proxy statement.
    - If the page contains a link to a page called Financial Information or similar, click on that link and navigate to the page.
    - Look for a link to the PDF version of the report specifically about annual report or proxy statement.
    ---

    ### Step 3: Return the PDF link
    - Return the URL for this PDF file.
    - In the final output, only return the URL of the PDF file.
    - Do not include any other information or text.
    ---
    ### Step 3: Close the Browser
    - Close the browser window.
    ---

    **Important:** Ensure efficiency and accuracy throughout the process.""".format(company_name)
    return task

def get_referer(url):
    """Return the referer (base URL) for a given URL."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"

# task = return_task("Moody's Analytics Inc")
# task = return_task("Billibilli")
# task = return_task("Sembcorp Industries")
# task = return_task("Blackrock Inc")
# task = return_task("bharti airtel")
# task = return_task("Xero")
# task = return_task("ICBC")
# task = return_task("Sinopec")
# task = return_task("Volkswagen")
# task = return_task("ADNOC")
task = return_task("Tata group")

# task = return_task("Saudi aramco")

browser = Browser()

llm = ChatOpenAI(
    model='gpt-4o', 
    temperature=0,
)
planner_llm = ChatOpenAI(model='o3-mini')

agent = Agent(
	task=task,
	llm=llm,
    planner_llm=planner_llm,
    use_vision_for_planner=False,
    planner_interval=4,
	browser=browser,
)

async def main():
    save_dir = "pdf"
    os.makedirs(save_dir, exist_ok=True)

    try:
        result = await agent.run()
    except Exception as agent_error:
        print("Error running agent:", agent_error)
        await browser.close()
        return

    extracted = result.extracted_content()
    if not extracted:
        print("No content extracted.")
        await browser.close()
        return

    extracted_url = extracted[-1].strip()
    if not extracted_url.startswith("http"):
        print("Extracted URL is invalid:", extracted_url)
        await browser.close()
        return

    final_url = extracted_url

    print(final_url)
    await browser.close()

if __name__ == '__main__':
	asyncio.run(main())