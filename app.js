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
const starsAmount = document.getElementById('stars-amount');
const tonAmount = document.getElementById('ton-amount');
const usdtAmount = document.getElementById('usdt-amount');
const resultCards = document.querySelectorAll('.result-card');

const MAX_INPUT_VALUE = 1000000000;
let currentCurrency = 'stars';

let rates = null;
const STARS_TO_USDT = 0.015;

// Fetch TON rate from external API
async function fetchTonRate() {
    try {
        const response = await fetch('https://api.split.tg/buy/ton_rate');
        if (response.ok) {
            const data = await response.json();
            return data.ton_rate;
        } else {
            console.error('Failed to fetch TON rate');
            return 3.15; // fallback rate
        }
    } catch (error) {
        console.error('Error fetching TON rate:', error);
        return 3.15; // fallback rate
    }
}

// Calculate all exchange rates
async function fetchRates() {
    try {
        const tonRate = await fetchTonRate();
        
        rates = {
            stars_to_usdt: STARS_TO_USDT,
            stars_to_ton: STARS_TO_USDT / tonRate,
            ton_to_usdt: tonRate,
            ton_to_stars: tonRate / STARS_TO_USDT,
            usdt_to_stars: 1 / STARS_TO_USDT,
            usdt_to_ton: 1 / tonRate
        };
        
        console.log('Rates updated:', rates);
    } catch (error) {
        console.error('Error calculating rates:', error);
    }
}

function getInputValue() {
    const text = amountInput.textContent.trim();
    return text === '' ? '' : text;
}

function setInputValue(value) {
    amountInput.textContent = value;
}

function validateInput(value) {
    const numValue = parseFloat(value);
    if (numValue > MAX_INPUT_VALUE) {
        amountInput.classList.add('error');
        
        // Vibration if supported
        if (navigator.vibrate) {
            navigator.vibrate([100, 50, 100]);
        }
        
        // Remove error class after animation
        setTimeout(() => {
            amountInput.classList.remove('error');
        }, 500);
        
        // Set input to max value
        setInputValue(MAX_INPUT_VALUE.toString());
        return MAX_INPUT_VALUE;
    }
    return numValue;
}

function updateActiveCard(activeCurrency) {
    resultCards.forEach(card => {
        if (card.dataset.currency === activeCurrency) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}

function formatNumber(num, decimals) {
    if (num === 0) return '0';
    const fixed = num.toFixed(decimals);
    return fixed.replace(/\.?0+$/, '');
}

function convert(amount) {
    // Always update active card, even without amount
    updateActiveCard(currentCurrency);
    
    if (!rates || amount === '' || isNaN(parseFloat(amount))) {
        starsAmount.textContent = '0';
        tonAmount.textContent = '0';
        usdtAmount.textContent = '0';
        return;
    }

    const parsedAmount = validateInput(amount);
    let starsValue, tonValue, usdtValue;

    switch (currentCurrency) {
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

    starsAmount.textContent = formatNumber(starsValue, 0);
    tonAmount.textContent = formatNumber(tonValue, 4);
    usdtAmount.textContent = formatNumber(usdtValue, 4);
}

function filterNumericInput(e) {
    // Allow: backspace, delete, tab, escape, enter, arrow keys
    if ([8, 9, 27, 13, 46, 37, 38, 39, 40].indexOf(e.keyCode) !== -1 ||
        // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
        (e.keyCode === 65 && (e.ctrlKey || e.metaKey)) ||
        (e.keyCode === 67 && (e.ctrlKey || e.metaKey)) ||
        (e.keyCode === 86 && (e.ctrlKey || e.metaKey)) ||
        (e.keyCode === 88 && (e.ctrlKey || e.metaKey))) {
        return;
    }
    
    // Get current text and selection
    const currentText = amountInput.textContent || '';
    const key = e.key;
    
    // Allow numbers and one decimal point
    if (!/[0-9.]/.test(key)) {
        e.preventDefault();
        return;
    }
    
    // Prevent multiple decimal points
    if (key === '.' && currentText.includes('.')) {
        e.preventDefault();
        return;
    }
}

async function init() {
    await fetchRates();
    
    // Handle input events for custom contenteditable div
    amountInput.addEventListener('input', () => {
        // Clean up non-numeric characters in real-time
        let currentText = amountInput.textContent || '';
        let cleanText = currentText.replace(/[^0-9.]/g, '');
        
        // Ensure only one decimal point
        const parts = cleanText.split('.');
        if (parts.length > 2) {
            cleanText = parts[0] + '.' + parts.slice(1).join('');
        }
        
        // Update content if it was cleaned
        if (currentText !== cleanText) {
            const cursorPos = window.getSelection().getRangeAt(0).startOffset;
            amountInput.textContent = cleanText;
            
            // Restore cursor position
            const range = document.createRange();
            const sel = window.getSelection();
            const textNode = amountInput.firstChild;
            if (textNode) {
                const newPos = Math.min(cursorPos, cleanText.length);
                range.setStart(textNode, newPos);
                range.collapse(true);
                sel.removeAllRanges();
                sel.addRange(range);
            }
        }
        
        const value = getInputValue();
        convert(value);
    });
    
    // Handle focus to show cursor
    amountInput.addEventListener('focus', () => {
        if (amountInput.textContent === '') {
            // Create a text node if empty to allow cursor positioning
            amountInput.textContent = '';
        }
        // Ensure cursor is positioned at the end
        setTimeout(() => {
            const range = document.createRange();
            const sel = window.getSelection();
            range.selectNodeContents(amountInput);
            range.collapse(false);
            sel.removeAllRanges();
            sel.addRange(range);
        }, 0);
    });
    
    // Handle click to focus and position cursor
    amountInput.addEventListener('click', () => {
        amountInput.focus();
    });
    
    // Filter numeric input
    amountInput.addEventListener('keydown', filterNumericInput);
    
    // Handle paste events
    amountInput.addEventListener('paste', (e) => {
        e.preventDefault();
        const paste = (e.clipboardData || window.clipboardData).getData('text');
        let numericPaste = paste.replace(/[^0-9.]/g, '');
        
        // Ensure only one decimal point
        const parts = numericPaste.split('.');
        if (parts.length > 2) {
            numericPaste = parts[0] + '.' + parts.slice(1).join('');
        }
        
        if (numericPaste) {
            // Clear current content and insert new
            amountInput.textContent = numericPaste;
            
            // Move cursor to end
            const range = document.createRange();
            const sel = window.getSelection();
            range.selectNodeContents(amountInput);
            range.collapse(false);
            sel.removeAllRanges();
            sel.addRange(range);
            
            // Trigger input event
            const inputEvent = new Event('input', { bubbles: true });
            amountInput.dispatchEvent(inputEvent);
        }
    });

    resultCards.forEach(card => {
        card.addEventListener('click', () => {
            currentCurrency = card.dataset.currency;
            const value = getInputValue();
            convert(value);
        });
    });

    // Set initial state
    updateActiveCard(currentCurrency);
    convert(getInputValue() || '0');
}

init();