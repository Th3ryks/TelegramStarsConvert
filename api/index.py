from flask import Flask, request
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class FragmentParser:
    def __init__(self):
        self.default_rates = {
            'stars_to_ton': 0.00519,
            'stars_to_usdt': 0.015,
            'ton_to_usdt': 2.89,
            'ton_to_stars': 192.68,
            'usdt_to_stars': 66.67,
            'usdt_to_ton': 0.346
        }
        
    def get_current_rates(self):
        logger.info("Returning default rates")
        return self.default_rates

price_parser = FragmentParser()

rates_cache = {
    'rates': None,
    'last_update': 0,
    'cache_ttl': 600
}

def get_rates():
    current_time = time.time()
    if rates_cache['rates'] is None or current_time - rates_cache['last_update'] > rates_cache['cache_ttl']:
        rates = price_parser.get_current_rates()
        rates_cache['rates'] = rates
        rates_cache['last_update'] = current_time
        return rates
    else:
        logger.info("Using cached rates")
        return rates_cache['rates']

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Currency Converter Stars/TON/USDT</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-color: #e0e0e0;
            --text-secondary: #a0a0a0;
            --border-color: #444;
            --input-bg: #2d2d2d;
            --accent-color: #0088cc;
            --accent-hover: #006da3;
            --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Roboto', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 16px 0;
        }

        .container {
            width: 100%;
            max-width: 100%;
            padding: 12px;
        }

        .converter-card {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            margin-bottom: 16px;
        }

        h1 {
            margin-bottom: 20px;
            color: var(--text-color);
            text-align: center;
            font-size: 24px;
            font-weight: 700;
        }

        .converter-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 24px;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        label {
            font-size: 16px;
            color: var(--text-secondary);
            font-weight: 500;
            margin-left: 4px;
        }

        input, select {
            height: 56px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            background-color: var(--input-bg);
            color: var(--text-color);
            padding: 0 16px;
            font-size: 18px;
            transition: border 0.2s;
            width: 100%;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--accent-color);
        }

        select {
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23a0a0a0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 16px center;
            padding-right: 48px;
        }

        .all-currencies {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            overflow: hidden;
            max-width: 100%;
        }

        .currency-card {
            background-color: var(--input-bg);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.2s;
            overflow: hidden;
            width: 100%;
        }

        .currency-card.active {
            background-color: var(--accent-color);
        }

        .currency-card:active {
            transform: scale(0.98);
        }

        .currency-info {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .currency-name {
            font-size: 16px;
            color: var(--text-secondary);
        }

        .currency-amount {
            font-size: 24px;
            font-weight: 700;
            color: var(--text-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        @media (max-width: 380px) {
            .container {
                padding: 8px;
            }

            .converter-card {
                padding: 16px;
            }

            h1 {
                font-size: 20px;
            }

            input, select {
                height: 48px;
                font-size: 16px;
            }

            .currency-amount {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="converter-card">
            <h1>Currency Converter</h1>
            <div class="converter-form">
                <div class="input-group">
                    <label for="amount">Amount</label>
                    <input type="number" id="amount" placeholder="Enter amount" min="0" step="any" value="0" inputmode="decimal">
                </div>
                
                <div class="input-group">
                    <label for="from-currency">Select Currency</label>
                    <select id="from-currency">
                        <option value="stars">Stars</option>
                        <option value="ton">TON</option>
                        <option value="usdt">USDT</option>
                    </select>
                </div>
            </div>
            
            <div class="all-currencies">
                <div class="currency-card" data-currency="stars">
                    <div class="currency-info">
                        <div class="currency-name">Stars</div>
                        <div class="currency-amount" id="stars-amount">0</div>
                    </div>
                </div>
                
                <div class="currency-card" data-currency="ton">
                    <div class="currency-info">
                        <div class="currency-name">TON</div>
                        <div class="currency-amount" id="ton-amount">0</div>
                    </div>
                </div>
                
                <div class="currency-card" data-currency="usdt">
                    <div class="currency-info">
                        <div class="currency-name">USDT</div>
                        <div class="currency-amount" id="usdt-amount">0</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const amountInput = document.getElementById('amount');
            const fromCurrencySelect = document.getElementById('from-currency');
            const currencyCards = document.querySelectorAll('.currency-card');
            
            const starsAmount = document.getElementById('stars-amount');
            const tonAmount = document.getElementById('ton-amount');
            const usdtAmount = document.getElementById('usdt-amount');

            let conversionRates = {
                'stars_to_ton': 0.00518,
                'stars_to_usdt': 0.015,
                'ton_to_stars': 193.05,
                'ton_to_usdt': 2.896,
                'usdt_to_stars': 66.67,
                'usdt_to_ton': 0.345
            };

            async function fetchRates() {
                try {
                    const response = await fetch('/rates');
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const data = await response.json();
                    conversionRates = data;
                    console.log("Rates updated:", conversionRates);
                    updateAllConversions();
                } catch (error) {
                    console.error("Failed to fetch rates:", error);
                }
            }

            async function convertViaAPI(fromCurrency, amount) {
                try {
                    const response = await fetch('/convert', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            from_currency: fromCurrency,
                            amount: amount
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    
                    const data = await response.json();
                    return data;
                } catch (error) {
                    console.error("Error during API conversion:", error);
                    return null;
                }
            }

            async function updateAllConversions() {
                const amount = parseFloat(amountInput.value) || 0;
                const fromCurrency = fromCurrencySelect.value;
                
                currencyCards.forEach(card => {
                    if (card.getAttribute('data-currency') === fromCurrency) {
                        card.classList.add('active');
                    } else {
                        card.classList.remove('active');
                    }
                });

                if (amount <= 0) {
                    starsAmount.textContent = '0';
                    tonAmount.textContent = '0';
                    usdtAmount.textContent = '0';
                    return;
                }

                try {
                    const apiResult = await convertViaAPI(fromCurrency, amount);
                    
                    if (apiResult && apiResult.result) {
                        if (apiResult.rates) {
                            conversionRates = apiResult.rates;
                        }
                        
                        starsAmount.textContent = formatNumber(apiResult.result.stars);
                        tonAmount.textContent = formatNumber(apiResult.result.ton);
                        usdtAmount.textContent = formatNumber(apiResult.result.usdt);
                    } else {
                        localConversion(fromCurrency, amount);
                    }
                } catch (error) {
                    console.error("Error updating conversions:", error);
                    localConversion(fromCurrency, amount);
                }
            }

            function localConversion(fromCurrency, amount) {
                let starsValue, tonValue, usdtValue;
                
                if (fromCurrency === 'stars') {
                    starsValue = amount;
                    tonValue = amount * conversionRates.stars_to_ton;
                    usdtValue = amount * conversionRates.stars_to_usdt;
                } else if (fromCurrency === 'ton') {
                    starsValue = amount * conversionRates.ton_to_stars;
                    tonValue = amount;
                    usdtValue = amount * conversionRates.ton_to_usdt;
                } else if (fromCurrency === 'usdt') {
                    starsValue = amount * conversionRates.usdt_to_stars;
                    tonValue = amount * conversionRates.usdt_to_ton;
                    usdtValue = amount;
                }

                starsAmount.textContent = formatNumber(starsValue);
                tonAmount.textContent = formatNumber(tonValue);
                usdtAmount.textContent = formatNumber(usdtValue);
            }

            function formatNumber(num) {
                if (!num) return '0';
                
                if (num >= 100) {
                    return num.toFixed(2);
                } else if (num >= 10) {
                    return num.toFixed(3);
                } else if (num >= 1) {
                    return num.toFixed(4);
                } else {
                    return num.toFixed(6);
                }
            }

            function initTelegramApp() {
                if (window.Telegram && window.Telegram.WebApp) {
                    const webApp = window.Telegram.WebApp;
                    webApp.ready();
                    document.documentElement.setAttribute('data-theme', 'dark');
                    webApp.expand();
                } else {
                    console.log("Telegram WebApp not detected, running in normal mode");
                }
            }

            amountInput.addEventListener('input', updateAllConversions);
            fromCurrencySelect.addEventListener('change', updateAllConversions);
            
            currencyCards.forEach(card => {
                card.addEventListener('click', () => {
                    fromCurrencySelect.value = card.getAttribute('data-currency');
                    updateAllConversions();
                });
            });

            fetchRates();
            initTelegramApp();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/rates')
def rates_api():
    return get_rates()

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    from_currency = data.get('from_currency')
    amount = float(data.get('amount', 0))
    
    rates = get_rates()
    
    if from_currency == 'stars':
        stars = amount
        ton = amount * rates['stars_to_ton']
        usdt = amount * rates['stars_to_usdt']
    elif from_currency == 'ton':
        stars = amount * rates['ton_to_stars']
        ton = amount
        usdt = amount * rates['ton_to_usdt']
    else:  # usdt
        stars = amount * rates['usdt_to_stars']
        ton = amount * rates['usdt_to_ton']
        usdt = amount
    
    return {
        'result': {
            'stars': stars,
            'ton': ton,
            'usdt': usdt
        },
        'rates': rates
    }

if __name__ == '__main__':
    # Run Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 