import streamlit as st
import openai
import ccxt
import pandas as pd
from dotenv import load_dotenv
import os

# Load secrets from .env or Render's environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")

# Setup KuCoin Futures connection
def get_kucoin_futures_client():
    return ccxt.kucoinfutures({
        'apiKey': KUCOIN_API_KEY,
        'secret': KUCOIN_API_SECRET,
        'password': KUCOIN_API_PASSPHRASE,
        'enableRateLimit': True
    })

# Fetch open positions
def fetch_open_positions(exchange):
    try:
        positions = exchange.fetch_positions()
        df = pd.DataFrame(positions)
        if df.empty:
            return pd.DataFrame([{"message": "No open positions."}])
        return df[["symbol", "side", "contracts", "entryPrice", "unrealizedPnl", "liquidationPrice"]]
    except Exception as e:
        return pd.DataFrame([{"error": str(e)}])

# Generate GPT response about your trades
def ask_gpt(question, context_data):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful crypto trading assistant."},
            {"role": "user", "content": f"My trade data:\n{context_data}\n\nQuestion:\n{question}"}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error talking to GPT: {e}"

# UI
st.set_page_config(page_title="KuCoin Futures Dashboard", layout="wide")
st.title("📊 KuCoin Futures Dashboard + ChatGPT Assistant")

# Load KuCoin and fetch positions
with st.spinner("Connecting to KuCoin..."):
    exchange = get_kucoin_futures_client()
    positions_df = fetch_open_positions(exchange)

# Show open positions
st.subheader("🔓 Open Positions")
st.dataframe(positions_df)

# Chat with GPT about your trades
st.subheader("🤖 Ask ChatGPT About Your Trades")
user_question = st.text_input("Ask a question about your trades:")
if st.button("Ask") and user_question:
    context_str = positions_df.to_csv(index=False)
    response = ask_gpt(user_question, context_str)
    st.markdown("**GPT Response:**")
    st.write(response)
