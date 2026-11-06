import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup

async def main():
    url = "https://www.wildberries.ru/catalog/961493176/detail.aspx?targetUrl=MI"
    
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        print("🌐 Открываем страницу...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Ждем 10 секунд...")
        await asyncio.sleep(10)
        
        # СОХРАНЯЕМ HTML КОД СТРАНИЦЫ
        html_content = await page.content()
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("✅ HTML сохранен в файл page.html")
        await browser.close()
        with open("page.html", "r", encoding = "utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        h2_tags = soup.find_all("h2")
        for tag in h2_tags:
            text = tag.get_text(strip=True)
            if "₽" in text:
                print(text)

if __name__ == "__main__":
    asyncio.run(main())