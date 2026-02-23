from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    """Page Object pour la page de connexion."""

    def load(self):
        self.open('/')

    def login(self, username: str, password: str):
        # remplit les champs et soumet
        self.fill(By.NAME, 'nom', username)
        self.fill(By.NAME, 'mdp', password)
        self.submit_form()
