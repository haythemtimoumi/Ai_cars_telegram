# 🚗 IA-CARS: Intelligent Car Advisor Bot 🤖
IA-CARS is your smart car-buying assistant. This Telegram bot analyzes used car deals in seconds by checking prices against real market data from top European sites. Just send the car details, and it'll tell you if it's a good deal or not - plus suggest better alternatives. Powered by AI and daily-updated listings, it takes the guesswork out of car shopping.
![Image](https://github.com/user-attachments/assets/7050486b-66bb-4814-af95-e469578e862b)
![Image](https://github.com/user-attachments/assets/30ff793d-2799-4d9f-a92d-c8e6f1ad9181)

## 🌟 Features

- **Smart Deal Analysis**: Random Forest model evaluates car deals
- **Multi-Source Data**: Scrapes from AutoScout24 (Germany) and Gumtree (UK)
- **Database**: PostgreSQL with 1300+ car listings
- **Dockerized**: Ready-to-deploy microservices architecture

## 🛠️ Tech Stack

| Component          | Technology                          |
|--------------------|-------------------------------------|
| Backend            | Python 3.11, FastAPI                |
| Web Scraping       | Selenium, undetected-chromedriver   |
| Database           | PostgreSQL 16                       |
| ML                 | Scikit-learn (Random Forest)        |
| Bot Framework      | python-telegram-bot v20.7           |
| Containerization   | Docker, Docker Compose              |

## 🚀 Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Telegram bot token from [@BotFather](https://t.me/BotFather)

