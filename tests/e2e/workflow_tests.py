import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestEndToEndWorkflows:
    """End-to-end workflow tests"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome driver for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_purchase_to_payment_workflow(self, driver):
        """Test complete purchase-to-payment workflow"""
        driver.get("http://localhost:3000/integration/workflows")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "workflow-manager"))
        )
        
        # Click P2P workflow
        p2p_card = driver.find_element(By.XPATH, "//div[contains(text(), 'Purchase to Payment')]")
        p2p_card.click()
        
        # Fill form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v-dialog"))
        )
        
        bill_number = driver.find_element(By.XPATH, "//input[@label='Bill Number']")
        bill_number.send_keys("E2E-001")
        
        # Submit workflow
        process_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Process Workflow')]")
        process_btn.click()
        
        # Verify results
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Workflow Results')]"))
        )
        
        success_alert = driver.find_element(By.CLASS_NAME, "v-alert--type-success")
        assert success_alert.is_displayed()
    
    def test_executive_dashboard_loads(self, driver):
        """Test executive dashboard loads correctly"""
        driver.get("http://localhost:3000/integration/dashboard")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "executive-dashboard"))
        )
        
        title = driver.find_element(By.TAG_NAME, "h1")
        assert "Executive Dashboard" in title.text
        
        kpi_cards = driver.find_elements(By.CLASS_NAME, "v-card")
        assert len(kpi_cards) >= 4