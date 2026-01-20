import streamlit as st
import os
import requests
import time


BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


def send_request_with_retry(url, files, max_retries=7):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, files=files)

            if response.status_code == 200:
                return response

            if response.status_code in [502, 503]:
                st.warning(
                    f"Server is waking up..(Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(15)
                continue

            return response

        except requests.exceptions.ConnectionError:
            st.warning(
                f"Connection lost, retrying..(Attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(5)
    return None


st.set_page_config(page_title="Receipt Parser", layout="centered")
st.title("AI Receipt Parser")

uploaded_file = st.file_uploader(
    "Upload a receipt (JPEG/PNG)", type=["jpg", "jpeg", "png"]
)


if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)

    if st.button("Scan Receipt", type="primary"):
        with st.spinner("Analyzing..."):
            try:
                files = {"file": ("receipt.jpg", uploaded_file, uploaded_file.type)}
                response = send_request_with_retry(
                    f"{BACKEND_URL}/receipts/scan", files=files
                )

                if response is not None and response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete")

                    raw_date = data.get("purchase_date")
                    if raw_date and "T" in raw_date:
                        display_date = raw_date.split("T")[0]
                    else:
                        display_date = raw_date or "Unknown"

                    currency = data.get("currency_symbol", "$")

                    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                    col1.metric("Store", data.get("store_name", "Unknown"))
                    col2.metric("Date", display_date)
                    col3.metric("Tax", f"{currency}{data.get('tax_amount', 0.0)}")
                    col4.metric("Total", f"{currency}{data.get('total_amount', 0.0)}")

                    confidence_val = data.get("scan_confidence", 0.0)
                    col5.metric("Confidence", f"{confidence_val * 100:.0f}%")

                    if data.get("items"):
                        st.write("### Purchased Items")
                        st.dataframe(data["items"], use_container_width=True)

                    with st.expander("See Raw JSON"):
                        st.json(data)
                elif response is not None:
                    st.error(f"Error {response.status_code}:{response.text}")
                else:
                    st.error("Server is taking too long to wake up please try again")

            except Exception as e:
                st.error(f"Connection Error: {e}")
