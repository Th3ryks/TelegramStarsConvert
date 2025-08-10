import time
import requests
from flask import Flask, render_template_string

""" --- CURRENCY CONVERTER CLASS --- """
class CurrencyConverter:
    def __init__(self):
        self.stars_to_usdt = 0.015
        self.rates_cache = {
            'rates': None,
            'last_update': 0,
            'cache_ttl': 600
        }
        
    def fetch_ton_rate(self) -> float:
        try:
            response = requests.get('https://api.split.tg/buy/ton_rate', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['ton_rate']
            else:
                print(f"Failed to fetch TON rate. Status code: {response.status_code}")
                return 3.3
        except Exception as e:
            print(f"Error fetching TON rate: {str(e)}")
            return 3.3
    
    def get_current_rates(self) -> dict:
        current_time = time.time()
        
        if (self.rates_cache['rates'] is None or 
            current_time - self.rates_cache['last_update'] > self.rates_cache['cache_ttl']):
            
            ton_rate = self.fetch_ton_rate()
            
            rates = {
                'stars_to_usdt': self.stars_to_usdt,
                'stars_to_ton': self.stars_to_usdt / ton_rate,
                'ton_to_usdt': ton_rate,
                'ton_to_stars': ton_rate / self.stars_to_usdt,
                'usdt_to_stars': 1 / self.stars_to_usdt,
                'usdt_to_ton': 1 / ton_rate
            }
            
            self.rates_cache['rates'] = rates
            self.rates_cache['last_update'] = current_time
            
            print("Updated rates with real TON price")
            return rates
        else:
            print("Using cached rates")
            return self.rates_cache['rates']

""" --- HTML TEMPLATE --- """
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⭐ Stars Converter</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #00d4ff;
            --accent-hover: #00b8e6;
            --border: #2a2a3e;
            --success: #00ff88;
            --warning: #ffaa00;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 400px;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
        }

        .title {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent) 0%, var(--success) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .subtitle {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .converter-card {
            background: var(--bg-card);
            border-radius: 20px;
            padding: 24px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }

        .input-section {
            margin-bottom: 16px;
        }

        .input-group {
            margin-bottom: 16px;
        }

        .label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input {
            width: 100%;
            height: 48px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 0 16px;
            font-size: 16px;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
        }

        .select {
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23a0a0a0' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 20px center;
            padding-right: 50px;
            cursor: pointer;
        }

        .results {
            display: grid;
            gap: 16px;
        }

        .result-card {
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 24px;
            border: 2px solid var(--border);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .result-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }

        .result-card.active {
            border-color: var(--accent);
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 255, 136, 0.1) 100%);
        }

        .currency-name {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .currency-amount {
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
        }

        /* Disable text selection and copy */
        html, body, .container, .converter-card, .results, .result-card, input, select {
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
            -webkit-touch-callout: none;
        }

        @media (max-width: 480px) {
            .converter-card {
                padding: 24px;
            }
            
            .title {
                font-size: 28px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">⭐ Stars Converter</h1>
            <p class="subtitle">Convert Telegram Stars to TON and USDT</p>
        </div>
        
        <div class="converter-card">
            <div class="input-section">
                <div class="input-group">
                    <label class="label" for="amount">Amount</label>
                    <input type="number" id="amount" class="input" placeholder="Enter amount" min="0" step="any">
                </div>
                
                <div class="input-group">
                    <label class="label" for="currency">From Currency</label>
                    <select id="currency" class="input select">
                        <option value="stars">⭐ Stars</option>
                        <option value="ton">💎 TON</option>
                        <option value="usdt">💵 USDT</option>
                    </select>
                </div>
            </div>
            
            <div class="results">
                <div class="result-card" data-currency="stars">
                    <div class="currency-name">⭐ Stars</div>
                    <div class="currency-amount" id="stars-amount">-</div>
                </div>
                <div class="result-card" data-currency="ton">
                    <div class="currency-name">💎 TON</div>
                    <div class="currency-amount" id="ton-amount">-</div>
                </div>
                <div class="result-card" data-currency="usdt">
                    <div class="currency-name">💵 USDT</div>
                    <div class="currency-amount" id="usdt-amount">-</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let tg = window.Telegram?.WebApp;
        if (tg) {
            tg.expand();
            tg.ready();
        }

        /* Disable copy/paste and context menu */
        document.addEventListener('copy', (e) => e.preventDefault());
        document.addEventListener('cut', (e) => e.preventDefault());
        document.addEventListener('paste', (e) => e.preventDefault());
        document.addEventListener('contextmenu', (e) => e.preventDefault());
        document.addEventListener('selectstart', (e) => e.preventDefault());
        document.addEventListener('dragstart', (e) => e.preventDefault());
        document.addEventListener('keydown', (e) => {
            const key = (e.key || '').toLowerCase();
            if ((e.ctrlKey || e.metaKey) && ['c', 'x', 'a', 's', 'p'].includes(key)) {
                e.preventDefault();
            }
        });

        const amountInput = document.getElementById('amount');
        const currencySelect = document.getElementById('currency');
        const starsAmount = document.getElementById('stars-amount');
        const tonAmount = document.getElementById('ton-amount');
        const usdtAmount = document.getElementById('usdt-amount');
        const resultCards = document.querySelectorAll('.result-card');

        const rates = {{ rates | tojson }};

        function updateActiveCard(activeCurrency) {
            resultCards.forEach(card => {
                if (card.dataset.currency === activeCurrency) {
                    card.classList.add('active');
                } else {
                    card.classList.remove('active');
                }
            });
        }

        function convert(amount, fromCurrency) {
            if (!rates || amount === '' || isNaN(parseFloat(amount))) {
                starsAmount.textContent = '-';
                tonAmount.textContent = '-';
                usdtAmount.textContent = '-';
                return;
            }

            const parsedAmount = parseFloat(amount);
            let starsValue, tonValue, usdtValue;

            switch (fromCurrency) {
                case 'stars':
                    starsValue = parsedAmount;
                    tonValue = parsedAmount * rates.stars_to_ton;
                    usdtValue = parsedAmount * rates.stars_to_usdt;
                    break;
                case 'ton':
                    tonValue = parsedAmount;
                    starsValue = parsedAmount * rates.ton_to_stars;
                    usdtValue = parsedAmount * rates.ton_to_usdt;
                    break;
                case 'usdt':
                    usdtValue = parsedAmount;
                    tonValue = parsedAmount * rates.usdt_to_ton;
                    starsValue = parsedAmount * rates.usdt_to_stars;
                    break;
            }

            starsAmount.textContent = starsValue.toFixed(0);
            tonAmount.textContent = tonValue.toFixed(4);
            usdtAmount.textContent = '$' + usdtValue.toFixed(2);

            updateActiveCard(fromCurrency);
        }

        function init() {
            amountInput.addEventListener('input', (e) => {
                convert(e.target.value, currencySelect.value);
            });

            currencySelect.addEventListener('change', (e) => {
                convert(amountInput.value, e.target.value);
            });

            resultCards.forEach(card => {
                card.addEventListener('click', () => {
                    currencySelect.value = card.dataset.currency;
                    convert(amountInput.value, card.dataset.currency);
                });
            });

            convert(amountInput.value || '0', currencySelect.value);
        }

        init();
    </script>
</body>
</html>
"""

""" --- FLASK APPLICATION --- """
app = Flask(__name__)
converter = CurrencyConverter()

@app.route('/')
def index():
    rates = converter.get_current_rates()
    return render_template_string(HTML_TEMPLATE, rates=rates)

""" --- MAIN FUNCTION --- """
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)