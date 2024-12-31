import streamlit as st
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from io import BytesIO
import requests

# Streamlit App
st.title("Flipkart Product Scraper By Kumaran 🫶")
st.write("Provide a product link and the number of pages to scrape.")
st.write("Connect with me on [LinkedIn](https://www.linkedin.com/in/elangkumaran)")

# Input fields
product_link = st.text_input("Product Link", "https://www.flipkart.com/search?q=mobile%20phone")
num_pages = st.number_input("Number of Pages to Scrape", min_value=1, max_value=10, value=4)

if st.button("Scrape"):
    # Initialize the Selenium WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Create progress bar
    progress = st.progress(0)

    # Initialize workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Flipkart Products"
    sheet.append(["Image", "Product Name", "Price", "Rating and Review", "Product Link"])  # Header row

    row = 2
    page_count = 0
    base_url = product_link

    while base_url and page_count < num_pages:
        # Navigate to the URL
        driver.get(base_url)
        time.sleep(random.uniform(3, 5))  # Wait for the page to load

        # Update progress bar
        progress.progress((page_count + 1) / num_pages)
        st.write(f"Scraping page: {base_url}")

        # Scrape product details
        products = driver.find_elements(By.CLASS_NAME, "_1AtVbE")
        st.write(f"Found {len(products)} products on page {page_count + 1}")

        for product in products:
            try:
                # Extract image URL
                image_tag = product.find_element(By.CLASS_NAME, "DByuf4")
                image_url = image_tag.get_attribute("src") if image_tag else None

                # Extract product name
                name_tag = product.find_element(By.CLASS_NAME, "KzDlHZ")
                product_name = name_tag.text.strip() if name_tag else "N/A"

                # Extract price
                price_tag = product.find_element(By.CLASS_NAME, "Nx9bqj _4b5DiR")
                product_price = price_tag.text.strip().replace(",", "") if price_tag else "N/A"

                # Extract rating and review
                rating_review_tag = product.find_element(By.CLASS_NAME, "hGSR34")
                if rating_review_tag:
                    rating_text = rating_review_tag.text
                    ratings, reviews = rating_text.split(' Ratings')[0], rating_text.split('Reviews')[0].split(' ')[-1]
                    rating_and_review = f"{ratings} Ratings, {reviews} Reviews"
                else:
                    rating_and_review = "N/A"

                # Extract product link
                link_tag = name_tag.find_element(By.XPATH, "..")  # Get parent anchor element
                product_link = "https://www.flipkart.com" + link_tag.get_attribute("href") if link_tag else "N/A"

                # Embed the image into Excel
                if image_url:
                    try:
                        img_data = requests.get(image_url).content
                        img = Image(BytesIO(img_data))
                        img.width = 80  # Resize to fit cell
                        img.height = 80
                        cell_address = f"A{row}"
                        sheet.add_image(img, cell_address)
                    except Exception as e:
                        st.warning(f"Error downloading image: {e}")

                # Add other product details to the Excel sheet
                sheet.cell(row=row, column=2, value=product_name)  # Product name
                sheet.cell(row=row, column=3, value=product_price)  # Price
                sheet.cell(row=row, column=4, value=rating_and_review)  # Rating and review
                sheet.cell(row=row, column=5, value=product_link)  # Product link

                row += 1
            except Exception as e:
                st.warning(f"Error extracting product information: {e}")

        # Find the next page link
        try:
            next_page = driver.find_element(By.CLASS_NAME, "_1LKTO3")
            base_url = next_page.get_attribute("href") if next_page else None
            page_count += 1
        except Exception as e:
            st.warning("No more pages found or an error occurred.")
            break

    # Save workbook to a BytesIO stream
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    # Allow download of the Excel file
    st.download_button(
        label="Download Excel File",
        data=output,
        file_name="Flipkart_Products.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Close the driver
    driver.quit()
    st.success("Scraping completed!")
