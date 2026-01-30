import fetch from "node-fetch";
import { JSDOM } from "jsdom";
import fs from "fs";

const START_ID = 0;
const END_ID = 574;
const BASE_URL = "https://www.a1cdp.com/index.php?opt=proddetail&product_id=";

const sleep = ms => new Promise(r => setTimeout(r, ms));
const results = [];

for (let productId = START_ID; productId <= END_ID; productId++) {
  const url = `${BASE_URL}${productId}`;

  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0"
      }
    });

    const html = await res.text();
    const dom = new JSDOM(html);
    const doc = dom.window.document;

    // Invalid product check
    if (doc.body.textContent.includes("Sorry, the product that you are trying to access")) {
      console.log(`❌ ${productId} invalid`);
      continue;
    }

    const get = selector =>
      doc.querySelector(selector)?.textContent.trim() || null;

    const product = {
      product_id: productId,
      product_code: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(3) > td.prd_2text"),
      stock_code: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(4) > td.prd_2text"),
      description: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(5) > td.longdesc"),
      dimensions: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(6) > td.prd_2text"),
      capacity: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(7) > td.prd_2text"),
      material: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(8) > td.prd_2text"),
      units_per_case: get("body > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table:nth-child(4) > tbody > tr:nth-child(1) > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr:nth-child(9) > td.prd_2text"),
      url
    };

    results.push(product);
    console.log(`✅ ${productId}`);

    // Be polite
    // await sleep(10);

  } catch (err) {
    console.log(`🔥 Error on ${productId}, skipping`);
  }
}

// Save JSON to disk
fs.writeFileSync("products.json", JSON.stringify(results, null, 2));
console.log(`\n🎉 Done. Saved ${results.length} products to products.json`);
