# ⭐ Stars Converter

🚀 A modern, asynchronous web application for converting Telegram Stars to TON and USDT currencies with real-time exchange rates.

## ✨ Features

- 🔄 **Real-time conversion** with live TON exchange rates
- 💰 **Fixed Stars rate** - 1 Star = $0.015 USD
- 🎨 **Modern UI** with beautiful dark theme and animations
- 📱 **Telegram Web App** integration ready
- ⚡ **Async/await** architecture for optimal performance
- 📊 **Caching system** for efficient API calls

## 🛠️ Tech Stack

- **Python 3.11+** with asyncio
- **aiohttp** for async web server
- **Environment variables** for configuration

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Th3ryks/TelegramStarsConvert.git
   cd TelegramStarsConvert
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

## ⚙️ Configuration

The application runs with default settings:
- **Host**: `0.0.0.0`
- **Port**: `5000`
- **TON Rate API**: `https://api.split.tg/buy/ton_rate`
- **Cache TTL**: `300 seconds`
- **Stars to USDT Rate**: `0.015`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | 🏠 Main converter interface |

## 💱 Exchange Rates

- **Stars to USD**: Fixed at $0.015 per star
- **TON to USD**: Real-time from Split.tg API
- **Stars to TON**: Calculated dynamically based on TON/USD rate

## 🎨 Interface Features

- 🌙 **Dark theme** optimized for Telegram
- 📱 **Responsive design** for all devices
- ✨ **Smooth animations** and hover effects
- 🎯 **Intuitive UX** with click-to-select currency cards
- 💫 **Gradient accents** and modern typography

## 🔒 Security

- ✅ Environment variables for sensitive data
- ✅ No hardcoded secrets or tokens
- ✅ Proper error handling and logging
- ✅ Input validation and sanitization

## 📝 License

MIT License - feel free to use this project for your own purposes! 🎉