# azure-ai-wise-accelerator

WISE is an AI and simulation based solution for enablement in the Financial Services Industry on Azure.

![Wise](images/WisePromo.jpg?raw=true)

## WISE

Financial advisors, wealth managers, and investment representatives need a secure and effective way to hone their skills. Managing diverse portfolios and answering a wide range of questions from clients and prospects requires expertise. Our AI-driven simulation platform offers a dynamic training environment where advisors can practice and receive actionable feedback to enhance their skills.

Every year, financial services companies onboard new sellers, aiming for a swift return on investment. With the constant addition of new products to their extensive portfolios, these companies need their teams to start selling immediately. Training front-office staff, support teams, and customer-facing personnel is a significant expense, often involving third-party vendors who charge thousands of dollars per trainee per week.

Our project uses real-time voice technology to provide a lifelike and cost-effective solution, enabling advisors to train efficiently while reducing overall enablement costs for financial services companies.

![Wise](images/WiseDeck.jpg?raw=true)

In this implementation, the end user is a financial advisor at Fidelity whose job is to position and sell the FIDI ETF to a skeptical customer, John. John will ask pointed questions, challenging the advisor to close the sale effectively. At the end of the interaction, the advisor will receive a score, along with the rationale behind it, suggestions for improvement, and a detailed fact-checking of all statements made.

![Wise](images/wise1.jpg?raw=true)

## How to run

### Start the backend

```
cd app\backend
.\.venv\scripts\activate
pip install -r requirements.txt
python app.py
```

### Start the frontend

```
cd app\frontend
npm install
npm run dev
```

#### Resources

This project was inspired and bootstrapped using this repo: https://github.com/john-carroll-sw/coffee-chat-voice-assistant
