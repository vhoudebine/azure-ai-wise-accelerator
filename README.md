# azure-ai-wise-accelerator

AI and simulation based solution for enablement in the Financial Services Industry on Azure
![Wise](images/logolarge.svg?raw=true)

## WISE

Financial advisors, wealth managers, and investment representatives need a secure and effective way to hone their skills. They manage diverse portfolios and must be prepared to answer a wide range of questions from clients and prospects. Our AI-driven simulation platform offers a dynamic training environment where advisors can practice and receive actionable feedback to enhance their expertise.

Every year, financial services companies onboard new sellers and aim for a swift return on investment. With the constant addition of new products to their extensive portfolios, these companies need their teams to start selling immediately. Training front-office staff, support teams, and customer-facing personnel is a significant expense, often involving third-party vendors who charge thousands of dollars per trainee per week.

Our project provides a cost-effective solution, enabling advisors to train efficiently while reducing overall enablement costs for financial services companies.

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
