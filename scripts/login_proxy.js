const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

puppeteer.use(StealthPlugin());

const PROXY_URL = process.env.PROXY_URL;
const COOKIES_PATH = path.join(__dirname, '../data/cookies.json');

(async () => {
    console.log("🚀 Starting Puppeteer with Stealth Plugin...");

    let launchArgs = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--window-size=1280,800'
    ];

    // Parse Proxy
    let proxyServer = "";
    let username = "";
    let password = "";

    if (PROXY_URL) {
        try {
            // Format: http://user:pass@host:port
            const url = new URL(PROXY_URL);
            proxyServer = `${url.protocol}//${url.hostname}:${url.port}`;
            username = url.username;
            password = url.password;

            console.log(`📡 Using Proxy: ${proxyServer}`);
            launchArgs.push(`--proxy-server=${proxyServer}`);
        } catch (e) {
            console.error("❌ Invalid Proxy URL format", e);
            return;
        }
    } else {
        console.warn("⚠️  NO PROXY URL FOUND in .env. Running direct connection (likely to be flagged if IP differs).");
    }

    const browser = await puppeteer.launch({
        headless: false,
        args: launchArgs,
        defaultViewport: null,
        ignoreHTTPSErrors: true
    });

    const page = await browser.newPage();

    // Set a very standard User-Agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    // Set viewport to a common resolution to avoid "bot" size
    await page.setViewport({ width: 1366, height: 768 });

    // Authenticate Proxy
    if (username && password) {
        console.log("🔐 Authenticating Proxy...");
        await page.authenticate({ username, password });
    }

    console.log("🌍 Navigating to X.com Login...");
    try {
        await page.goto('https://x.com/i/flow/login', { waitUntil: 'networkidle2', timeout: 60000 });
    } catch (e) {
        console.error("⚠️ Navigation timeout/error:", e.message);
    }

    console.log("\n==================================================");
    console.log("👉 ACTION REQUIRED: Please log in manually in the browser window.");
    console.log("👉 Solve any captchas (Arkose/Funcaptcha) if they appear.");
    console.log("==================================================\n");

    // Wait for redirect to home or profile to confirm login
    try {
        await page.waitForFunction(
            () => window.location.href.includes('/home') || window.location.href.includes('/messages'),
            { timeout: 0 } // Wait indefinitely until user logs in
        );
        console.log("✅ Login detected (Home/Messages URL)!");

        // Wait a bit for cookies to settle
        await new Promise(r => setTimeout(r, 3000));

        // Get Cookies
        const client = await page.target().createCDPSession();
        const cookies = (await client.send('Network.getAllCookies')).cookies;

        // Filter specific keys for twikit (auth_token, ct0)
        const relevantCookies = {};
        cookies.forEach(c => {
            if (c.name === 'auth_token' || c.name === 'ct0') {
                relevantCookies[c.name] = c.value;
            }
        });

        if (relevantCookies.auth_token && relevantCookies.ct0) {
            // Ensure data dir exists
            const dataDir = path.dirname(COOKIES_PATH);
            if (!fs.existsSync(dataDir)) {
                fs.mkdirSync(dataDir, { recursive: true });
            }

            fs.writeFileSync(COOKIES_PATH, JSON.stringify(relevantCookies, null, 4));
            console.log(`🍪 Cookies saved successfully to: ${COOKIES_PATH}`);
            console.log("🎉 You can now close the browser.");
        } else {
            console.error("❌ Failed to capture 'auth_token' or 'ct0'. Did you fully log in?");
        }

    } catch (e) {
        console.error("❌ Error during wait for login:", e);
    }

    // Keep open for a moment
    await new Promise(r => setTimeout(r, 5000));
    await browser.close();
})();
