from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from requests.exceptions import Timeout, RequestException
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret_key"

# Alchemy Solana RPC Endpoint
SOLANA_RPC_URL = os.getenv("SOL_RPC")

@app.route('/', methods=['GET', 'POST'])
def home():
    wallet_address = None
    balance_sol = None
    balance_lamports = None
    api_version = None
    slot = None
    error = None

    if request.method == 'POST':
        wallet_address = request.form.get('wallet_address')

        if not wallet_address:
            flash('Please enter a valid wallet address!', 'error')
            return redirect(url_for('home'))

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }

        try:
            response = requests.post(SOLANA_RPC_URL, json=payload, timeout=10)
            response.raise_for_status()
            response_data = response.json()

            if 'error' in response_data:
                error = response_data['error']['message']
            else:
                result = response_data.get("result", {})
                balance_lamports = result.get("value", 0)
                balance_sol = balance_lamports / 10**9  # Converting lamports to SOL

                context = result.get("context", {})
                api_version = context.get("apiVersion", "N/A")
                slot = context.get("slot", "N/A")

        except Timeout:
            error = "The request timed out. Please try again later."
        except RequestException as e:
            error = f"An error occurred while fetching data: {str(e)}"
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"

    return render_template(
        'index.html', 
        wallet_address=wallet_address,
        balance_sol=balance_sol,
        balance_lamports=balance_lamports,
        api_version=api_version,
        slot=slot,
        error=error
    )

if __name__ == '__main__':
    app.run(debug=True)