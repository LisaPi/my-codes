from selenium import webdriver
import unittest

class PicosTestCase(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)

    def testPageTitle(self):
        self.browser.get('http://10.10.50.138/')
        self.assertIn('Pica8 OVS Switch Management Panel', self.browser.title)

if __name__ == '__main__':
    unittest.main(verbosity=2)

