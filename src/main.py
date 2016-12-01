import getpass
import requests
from bs4 import BeautifulSoup


class Main():
    @staticmethod
    def get_token():
        response = requests.get("https://leetcode.com/accounts/login/")
        return BeautifulSoup(response.content, "html.parser").findAll(attrs={"name": "csrfmiddlewaretoken"})[0]['value']

    @staticmethod
    def get_credentials():
        return {"username": input("Username: "), "password": getpass.getpass("Password: ")}

    @staticmethod
    def login(credentials, token):
        response = requests.post("https://leetcode.com/accounts/login/",
                                 data={"login": credentials['username']
                                     , "password": credentials['password']
                                     , "csrfmiddlewaretoken": token},
                                 headers={"Content-Type": "application/x-www-form-urlencoded"
                                     , "Cookie": "csrftoken=" + token + "; _ga=GA1.2.1164685322.1480633056"
                                     , "Referer": "https://leetcode.com/accounts/login/"})
        print(response.content)


def main():
    credentials = Main.get_credentials()
    token = Main.get_token()
    Main.login(credentials, token)


if __name__ == "__main__":
    main()
