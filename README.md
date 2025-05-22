# Zoho Books & Lark Approval Integration

This Flask project automates Lark approval flows when a Sales Order is created or updated in Zoho Books.

## Features

- Receive Zoho Books webhook on new Sales Order
- Send approval request to Lark
- After Lark approval, update status back to Zoho Books

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourname/zoho-lark-integration.git
   cd zoho-lark-integration
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Run the server:
   ```bash
   python app.py
   ```

5. Deploy to Render or any other platform and use your endpoint in Zoho Webhook and Lark approval callback.

## Webhooks

- **Zoho Books Webhook**: POST `/zoho-sales-order`
- **Lark Approval Callback**: POST `/lark-callback`