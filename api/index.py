from flask import Flask, request, jsonify
import time
import logging
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class FragmentParser:
    """Parser for handling currency conversion rates and fetching real-time TON price"""
    def __init__(self):
        self.default_rates = {
            'stars_to_ton': 0.005432,
            'stars_to_usdt': 0.015,
            'ton_to_usdt': None,
            'ton_to_stars': None,
            'usdt_to_stars': 66.67,
            'usdt_to_ton': None
        }
        
    def get_current_rates(self):
        """Fetches current TON rate and calculates all conversion rates"""
        try:
            response = requests.get('https://api.split.tg/buy/ton_rate')
            if response.status_code == 200:
                ton_rate = response.json()['ton_rate']
                self.default_rates['ton_to_usdt'] = ton_rate
                self.default_rates['usdt_to_ton'] = 1 / ton_rate
                self.default_rates['ton_to_stars'] = 1 / self.default_rates['stars_to_ton']
            else:
                logger.error(f"Failed to fetch TON rate. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching TON rate: {str(e)}")
            self.default_rates['ton_to_usdt'] = 2.77
            self.default_rates['usdt_to_ton'] = 1 / 2.77
            self.default_rates['ton_to_stars'] = 1 / self.default_rates['stars_to_ton']
        
        logger.info("Returning rates with real TON price")
        return self.default_rates

price_parser = FragmentParser()

rates_cache = {
    'rates': None,
    'last_update': 0,
    'cache_ttl': 600
}

def get_rates():
    """Returns current rates from cache or fetches new ones if cache expired"""
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
                    <input type="number" id="amount" placeholder="Enter amount" min="0" step="any" inputmode="decimal">
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
                        <div class="currency-amount" id="stars-amount">-</div>
                    </div>
                </div>
                <div class="currency-card" data-currency="ton">
                    <div class="currency-info">
                        <div class="currency-name">TON</div>
                        <div class="currency-amount" id="ton-amount">-</div>
                    </div>
                </div>
                <div class="currency-card" data-currency="usdt">
                    <div class="currency-info">
                        <div class="currency-name">USDT</div>
                        <div class="currency-amount" id="usdt-amount">-</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.enableClosingConfirmation();
        tg.ready();

        const amountInput = document.getElementById('amount');
        const fromCurrencySelect = document.getElementById('from-currency');
        const starsAmount = document.getElementById('stars-amount');
        const tonAmount = document.getElementById('ton-amount');
        const usdtAmount = document.getElementById('usdt-amount');

        let rates = {};
        let lastConversion = {
            amount: 0,
            fromCurrency: 'stars'
        };

        async function fetchRates() {
            try {
                const response = await fetch('/rates');
                rates = await response.json();
            } catch (error) {
                console.error('Error fetching rates:', error);
            }
        }

        function convert(amount, fromCurrency) {
            if (!rates || amount === '') {
                starsAmount.textContent = '-';
                tonAmount.textContent = '-';
                usdtAmount.textContent = '-';
                return;
            }

            const parsedAmount = parseFloat(amount);
            if (isNaN(parsedAmount)) {
                return;
            }

            let starsValue, tonValue, usdtValue;

            switch (fromCurrency) {
                case 'stars':
                    starsValue = parsedAmount;
                    tonValue = parsedAmount * rates.stars_to_ton;
                    usdtValue = tonValue * rates.ton_to_usdt;
                    break;
                case 'ton':
                    tonValue = parsedAmount;
                    starsValue = parsedAmount * rates.ton_to_stars;
                    usdtValue = parsedAmount * rates.ton_to_usdt;
                    break;
                case 'usdt':
                    usdtValue = parsedAmount;
                    tonValue = parsedAmount * rates.usdt_to_ton;
                    starsValue = tonValue * rates.ton_to_stars;
                    break;
            }

            starsAmount.textContent = starsValue.toFixed(2);
            tonAmount.textContent = tonValue.toFixed(4);
            usdtAmount.textContent = usdtValue.toFixed(2);

            const cards = document.querySelectorAll('.currency-card');
            cards.forEach(card => {
                if (card.dataset.currency === fromCurrency) {
                    card.classList.add('active');
                } else {
                    card.classList.remove('active');
                }
            });
        }

        async function init() {
            await fetchRates();
            setInterval(fetchRates, 60000);

            amountInput.addEventListener('input', (e) => {
                lastConversion.amount = e.target.value;
                convert(e.target.value, fromCurrencySelect.value);
            });

            fromCurrencySelect.addEventListener('change', (e) => {
                lastConversion.fromCurrency = e.target.value;
                convert(amountInput.value, e.target.value);
            });

            const cards = document.querySelectorAll('.currency-card');
            cards.forEach(card => {
                card.addEventListener('click', () => {
                    fromCurrencySelect.value = card.dataset.currency;
                    convert(amountInput.value, card.dataset.currency);
                });
            });
        }

        init();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Renders the main currency converter page"""
    return HTML_TEMPLATE

@app.route('/rates')
def rates_api():
    """Returns current conversion rates for all supported currencies"""
    return jsonify(get_rates())

@app.route('/convert', methods=['POST'])
def convert():
    """Converts amount between specified currencies using current rates"""
    data = request.get_json()
    amount = float(data['amount'])
    from_currency = data['from_currency']
    to_currency = data['to_currency']
    
    rates = get_rates()
    result = None
    
    if from_currency == to_currency:
        result = amount
    elif from_currency == 'stars' and to_currency == 'ton':
        result = amount * rates['stars_to_ton']
    elif from_currency == 'stars' and to_currency == 'usdt':
        result = amount * rates['stars_to_usdt']
    elif from_currency == 'ton' and to_currency == 'stars':
        result = amount * rates['ton_to_stars']
    elif from_currency == 'ton' and to_currency == 'usdt':
        result = amount * rates['ton_to_usdt']
    elif from_currency == 'usdt' and to_currency == 'stars':
        result = amount * rates['usdt_to_stars']
    elif from_currency == 'usdt' and to_currency == 'ton':
        result = amount * rates['usdt_to_ton']
    
    return jsonify({'result': result})

@app.route('/ton_rate')
def ton_rate():
    """Fetches current TON price in USD from split.tg API"""
    try:
        response = requests.get('https://api.split.tg/buy/ton_rate')
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            logger.error(f"Failed to fetch TON rate. Status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch TON rate"}), 500
    except Exception as e:
        logger.error(f"Error fetching TON rate: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 