import streamlit as st
import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

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
                response = requests.post(f"{BACKEND_URL}/receipts/scan", files=files)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete")

                    raw_date = data.get("purchase_date")
                    if raw_date and "T" in raw_date:
                        display_date = raw_date.split("T")[0]
                    else:
                        display_date = raw_date or "Unknown"

                    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                    col1.metric("Store", data.get("store_name", "Unknown"))
                    col2.metric("Date", display_date)
                    col3.metric("Tax", f"${data.get('tax_amount', 0.0)}")
                    col4.metric("Total", f"${data.get('total_amount', 0.0)}")

                    confidence_val = data.get("scan_confidence", 0.0)
                    col5.metric("Confidence", f"{confidence_val * 100:.0f}%")

                    if data.get("items"):
                        st.write("### Purchased Items")
                        st.dataframe(data["items"], use_container_width=True)

                    with st.expander("See Raw JSON"):
                        st.json(data)

                else:
                    st.error(f"Error {response.status_code}:{response.text}")

            except Exception as e:
                st.error(f"Connection Error: {e}")
