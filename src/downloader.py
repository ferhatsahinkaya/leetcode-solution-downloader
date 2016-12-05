import re
import requests
from bs4 import BeautifulSoup

import constants
from input import Input


class Downloader:
    def get_token(self):
        response = self.session.get(constants.LOGIN_URL)
        return BeautifulSoup(response.content, "html.parser").find(attrs={"name": "csrfmiddlewaretoken"})['value']

    def login(self):
        self.session.post(constants.LOGIN_URL,
                          data={"login": self.credentials['username']
                              , "password": self.credentials['password']
                              , "csrfmiddlewaretoken": self.get_token()},
                          headers={"Referer": constants.LOGIN_URL})

    def get_tags(self):
        response = self.session.get(constants.ALGORITHMS_URL)
        return [tag['href'] for tag in
                BeautifulSoup(response.content, "html.parser").findAll("a", attrs={"href": re.compile(r"/tag/*/")})]

    def get_questions(self, tag):
        response = self.session.get(constants.BASE_URL + tag)
        questions = BeautifulSoup(response.content, "html.parser") \
            .find("table", attrs={"id": "question_list"}).tbody.findAll("tr")
        return [question.find("a", attrs={"href": re.compile(r"/problems/*/")})['href'] for question in
                questions if question.find("span", attrs={"class": "ac"}) is not None]

    def save_solution(self, question, submission):
        response = self.session.get(constants.BASE_URL + submission)
        soup = BeautifulSoup(response.content, "html.parser")
        file_name = soup.find("a", attrs={"href": question}).text
        tag = soup.find("script", text=re.compile(r"submissionCode:*")).text
        code_type = Downloader.get_attribute_value(tag, "getLangDisplay", "submissionCode")
        code = Downloader.get_attribute_value(tag, "submissionCode", "editCodeUrl")
        print("Saving solution for '" + file_name + "'")
        with open("{0}/{1}.{2}".format(self.path, file_name, code_type), 'w') as file_:
            file_.write(code)

    def save_solutions(self, questions):
        for question in questions:
            response = self.session.get(constants.BASE_URL + question + "submissions")
            submissions = BeautifulSoup(response.content, "html.parser").findAll("a", attrs={
                "href": re.compile(r"/submissions/detail/*/")})
            self.save_solution(question, Downloader.get_latest_accepted_submission(submissions))

    def download(self):
        self.login()
        for tag in self.get_tags():
            print("Saving solutions under '" + tag + "'")
            self.save_solutions(self.get_questions(tag))

    @staticmethod
    def get_latest_accepted_submission(submissions):
        return [submission for submission in submissions if submission.strong][0]['href']

    @staticmethod
    def get_attribute_value(tag, attribute, next_attribute):
        attribute_value = tag[tag.index(attribute + ": '"):tag.index(next_attribute + ": '")]
        return attribute_value[attribute_value.index("'") + 1:attribute_value.rindex("'")].encode('utf8').decode(
            'unicode_escape')

    def __init__(self):
        self.session = requests.Session()
        self.credentials = Input.get_credentials()
        self.path = Input.get_path()
