from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time, csv

# Setup
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
driver.get("https://4over.com/customer/account/login/")

# Login
driver.find_element(By.ID, "email").send_keys("admin@printitprints.com")
driver.find_element(By.ID, "pass").send_keys("ITFactor@!1")
driver.find_element(By.ID, "send2").click()
wait.until(EC.url_contains("/customer/account"))

# Go to product page
driver.get("https://4over.com/pearl-greeting-cards")
wait.until(EC.presence_of_element_located((By.ID, "product-options-wrapper")))

# CSV setup
csv_file = open("smart_4over_data.csv", mode="w", newline="", encoding="utf-8")
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
                    global header_written
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

# Done
csv_file.close()
driver.quit()
print("✅ Done scraping all valid combinations.")
