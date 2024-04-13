import puppeteer from "puppeteer";

export async function openBrowser(browser) {
  if (browser !== null) {
    await browser.close();
  }
  // Launch the browser and open a new blank page
  browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // Navigate the page to a URL
  await page.goto("https://developer.chrome.com/");

  // Set screen size
  await page.setViewport({ width: 1080, height: 1024 });
}
