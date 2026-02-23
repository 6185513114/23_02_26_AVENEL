from selenium.webdriver.common.by import By


class BasePage:
    """Fonctions utilitaires communes aux pages."""

    def __init__(self, driver):
        self.driver = driver

    def open(self, path: str = '/'):
        self.driver.get(f'http://127.0.0.1:5000{path}')

    def find(self, by: By, value: str):
        return self.driver.find_element(by, value)

    def fill(self, by: By, value: str, text: str):
        el = self.find(by, value)
        el.clear()
        el.send_keys(text)

    def submit_form(self):
        # soumet le premier form présent
        self.driver.find_element(By.TAG_NAME, 'form').submit()
