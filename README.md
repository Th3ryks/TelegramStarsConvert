# ⭐ Stars Converter

🚀 A modern static web application for converting Telegram Stars to TON and USDT currencies with real-time exchange rates.

## ✨ Features

- 🔄 **Real-time conversion** with live TON exchange rates
- 💰 **Fixed Stars rate** - 1 Star = $0.015 USD
- 🎨 **Modern UI** with beautiful dark theme and animations
- 📱 **Telegram Web App** integration ready
- ⚡ **Pure client-side** - no server required
- 📊 **Direct API calls** to external exchange rate services
- 🗂️ **Clean structure** with separated HTML, CSS, and JavaScript

## 🛠️ Tech Stack

- **HTML5** for structure
- **CSS3** with modern styling and animations
- **Vanilla JavaScript** for all functionality
- **External APIs** for real-time exchange rates

## 📁 Project Structure

```
StarsConvert/
├── index.html          # Main HTML page
├── style.css           # CSS styles and animations
├── app.js              # JavaScript functionality
├── requirements.txt    # No dependencies (static site)
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Th3ryks/TelegramStarsConvert.git
   cd TelegramStarsConvert
   ```

2. **Open the application**
   Simply open `index.html` in your web browser, or use a local server:
   ```bash
   # Using Python's built-in server
   python3 -m http.server 8000
   
   # Using Node.js live-server (if installed)
   npx live-server
   
   # Or just double-click index.html
   ```

3. **Access the application**
   ```
   http://localhost:8000
   ```

## ⚙️ Configuration

The application uses these settings:
- **TON Rate API**: `https://api.split.tg/buy/ton_rate`
- **Stars to USDT Rate**: `0.015` (fixed rate)
- **Fallback TON Rate**: `3.15` USDT (if API fails)
- **Client-side**: All calculations performed in browser

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

MIT License - feel free to use this project for your own purposes! 🎉# Test commit
