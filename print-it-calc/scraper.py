from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time, csv, re

# Setup
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Login function
def login():
    driver.get("https://4over.com/customer/account/login/")
    driver.find_element(By.ID, "email").send_keys("admin@printitprints.com")
    driver.find_element(By.ID, "pass").send_keys("ITFactor@!1")
    driver.find_element(By.ID, "send2").click()
    wait.until(EC.url_contains("/customer/account"))

# Function to extract product name from URL
def extract_product_name(url):
    # Extract the last part of the URL path
    product_name = url.split('/')[-1]
    # Clean up the product name for filename
    product_name = re.sub(r'[^\w\-_\.]', '_', product_name)
    return product_name

# Function to scrape a single product
def scrape_product(product_url):
    print(f"Scraping: {product_url}")
    
    # Go to product page
    driver.get(product_url)
    wait.until(EC.presence_of_element_located((By.ID, "product-options-wrapper")))
    
    # Extract product name for CSV filename
    #product_name = extract_product_name(product_url)
    product_name = extract_product_name(product_url).replace('-', ' ')
    csv_filename = f"{product_name} 4over_data.csv"
    
    # CSV setup
    csv_file = open(csv_filename, mode="w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    header_written = False
    
    # Recursive function
    def recurse_dropdowns(depth=0, selected_options=[]):
        dropdowns = driver.find_elements(By.CLASS_NAME, "super-attribute-select")
        
        # If we've selected all dropdowns, extract pricing
        if depth >= len(dropdowns):
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "runsizes-table")))
                rows = driver.find_elements(By.CSS_SELECTOR, ".runsizes-table .runsizes_row")

                for row in rows:
                    spans = row.find_elements(By.TAG_NAME, "span")
                    if len(spans) >= 3:
                        data = selected_options + [
                            spans[0].text.strip(),  # RunSize
                            spans[1].text.strip().replace("$", ""),
                            spans[2].text.strip().replace("$", "")
                        ]
                        nonlocal header_written
                        if not header_written:
                            labels = [get_label_text(dd) for dd in dropdowns]
                            writer.writerow(labels + ["RunSize", "UnitPrice", "TotalPrice"])
                            header_written = True
                        writer.writerow(data)
            except:
                print("No pricing for:", selected_options)
            return

        # Current dropdown
        current_dropdown = dropdowns[depth]

        # Skip if disabled
        if not current_dropdown.is_enabled():
            recurse_dropdowns(depth + 1, selected_options + ["SKIPPED"])
            return

        select = Select(current_dropdown)
        options = [o for o in select.options if o.get_attribute("value")]

        for option in options:
            value = option.get_attribute("value")
            text = option.text.strip()

            # Select option via JS + trigger change
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                current_dropdown, value
            )

            time.sleep(2)  # Wait for dependent dropdown to update
            recurse_dropdowns(depth + 1, selected_options + [text])

    # Helper to get label for each dropdown
    def get_label_text(dropdown):
        try:
            label = dropdown.find_element(By.XPATH, "../preceding-sibling::label/span")
            return label.text.strip().replace("*", "")
        except:
            return "Option"

    # Start recursion
    recurse_dropdowns()
    
    # Close CSV file
    csv_file.close()
    print(f"✅ Completed scraping for {product_name}. Data saved to {csv_filename}")

# Main execution
if __name__ == "__main__":
    # Login first
    login()
    
    # Get number of products from admin
    try:
        num_products = int(input("Enter the number of products to scrape: "))
    except ValueError:
        print("Please enter a valid number.")
        driver.quit()
        exit()
    
    # Get product URLs from admin
    product_urls = []
    for i in range(num_products):
        url = input(f"Enter product URL {i+1}: ").strip()
        if url:
            product_urls.append(url)
    
    # Scrape each product
    for i, url in enumerate(product_urls, 1):
        print(f"\n--- Processing Product {i}/{len(product_urls)} ---")
        try:
            scrape_product(url)
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            continue
    
    # Done
    driver.quit()
    print(f"\n🎉 All done! Scraped {len(product_urls)} products successfully.")
