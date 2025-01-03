import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape Flipkart product details
def scrape_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    
    for item in soup.find_all('div', {'class': '_1AtVbE'}):
        product_name = item.find('a', {'class': 'IRpwTa'})
        product_mrp = item.find('div', {'class': '_30jeq3'})
        product_rate = item.find('div', {'class': '_3I9_wc'})
        product_rating = item.find('div', {'class': '_3LWZlK'})
        product_link = item.find('a', {'class': '_1fQZEK'})
        product_image = item.find('img', {'class': '_396cs4'})
        
        if product_name and product_mrp:
            products.append({
                'Name': product_name.get_text(),
                'MRP': product_mrp.get_text(),
                'Rate': product_rate.get_text() if product_rate else None,
                'Rating': product_rating.get_text() if product_rating else None,
                'Link': 'https://www.flipkart.com' + product_link['href'] if product_link else None,
                'Image': product_image['src'] if product_image else None
            })
    
    return products

# Streamlit app
st.title("Flipkart Product Scraper")

query = st.text_input("Enter product search term:")

if st.button("Scrape"):
    if query:
        products = scrape_flipkart(query)
        if products:
            df = pd.DataFrame(products)
            st.write(df)
            
            # Download as Excel
            df.to_excel("flipkart_products.xlsx", index=False)
            with open("flipkart_products.xlsx", "rb") as file:
                btn = st.download_button(
                    label="Download Excel",
                    data=file,
                    file_name="flipkart_products.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.write("No products found.")
    else:
        st.write("Please enter a product search term.")
