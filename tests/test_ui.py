import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(BASE_URL)

        text_input = driver.find_element(By.ID, "text-input")
        text_input.send_keys("The cinematography was breathtaking and the performances were outstanding")

        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()

        wait = WebDriverWait(driver, 10)
        result = wait.until(
            EC.presence_of_element_located((By.ID, "result-output"))
        )
        wait.until(lambda d: d.find_element(By.ID, "result-output").text.strip() != "")

        result_text = driver.find_element(By.ID, "result-output").text
        assert result_text.strip() != ""
        assert any(word in result_text for word in ["POSITIVE", "NEGATIVE", "Confidence"])
    finally:
        driver.quit()