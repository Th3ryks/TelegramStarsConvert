# Currency Converter (Stars/TON/USDT)

A simple web application for converting between Stars, TON, and USDT cryptocurrencies.

## Features

- Real-time currency conversion
- Support for Stars, TON, and USDT
- Clean and modern dark theme interface
- Telegram Mini App integration
- Responsive design

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Th3ryks/TelegramStarsConvert.git
cd TelegramStarsConvert
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python api/index.py
```

## Usage

1. Enter the amount you want to convert
2. Select the source currency (Stars, TON, or USDT)
3. The converted amounts will be displayed automatically in all currencies

## API Endpoints

- `GET /rates` - Get current exchange rates
- `POST /convert` - Convert between currencies
  - Request body: `{ "from_currency": "stars", "amount": 100 }`
  - Supported currencies: "stars", "ton", "usdt"

## Technologies Used

- Python (Flask)
- HTML/CSS/JavaScript
- Telegram Mini App API 