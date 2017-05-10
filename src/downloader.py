import json
import os
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

    def save_solution_file(self, problem_set, file_name, code_type, code):
        if not os.path.exists(self.path + "/" + problem_set):
            print("Creating folder '" + self.path + "/" + problem_set + "'")
            os.makedirs(self.path + "/" + problem_set)
        print("Saving solution for '" + file_name + "'")
        with open("{0}/{1}/{2}.{3}".format(self.path, problem_set, file_name, code_type), 'w') as file_:
            file_.write(code)

    def save_solution(self, problem_set, question, submission):
        response = self.session.get(constants.BASE_URL + submission)
        soup = BeautifulSoup(response.content, "html.parser")
        file_name = soup.find("a", attrs={"href": "/problems/" + question + "/"}).text
        tag = soup.find("script", text=re.compile(r"submissionCode:*")).text
        code_type = Downloader.get_attribute_value(tag, "getLangDisplay", "submissionCode")
        code = Downloader.get_attribute_value(tag, "submissionCode", "editCodeUrl")
        self.save_solution_file(problem_set, file_name, code_type, code)

    def save_solutions(self, problem_set, questions):
        for question in questions:
            response = self.session.get(constants.SUBMISSIONS_URL + question + constants.SUBMISSION_PARAMETERS)
            accepted_submissions = self.get_latest_accepted_submission(json.loads(response.content))
            if accepted_submissions:
                self.save_solution(problem_set, question, accepted_submissions[0]["url"])
            else:
                print("No accepted solution found for " + question)

    def download(self):
        self.login()
        for problem_set in constants.PROBLEM_SETS:
            response = self.session.get(constants.PROBLEMS_URL + problem_set)
            self.save_solutions(problem_set, self.get_accepted_questions(json.loads(response.content)))

    @staticmethod
    def get_accepted_questions(problems):
        return [question['stat']['question__title_slug'] for question in
                problems['stat_status_pairs'] if question['status'] == "ac"]

    @staticmethod
    def get_latest_accepted_submission(submissions):
        return [submission for submission in submissions["submissions_dump"] if
                submission['status_display'] == 'Accepted']

    @staticmethod
    def get_attribute_value(tag, attribute, next_attribute):
        attribute_value = tag[tag.index(attribute + ": '"):tag.index(next_attribute + ": '")]
        return attribute_value[attribute_value.index("'") + 1:attribute_value.rindex("'")].encode('utf8').decode(
            'unicode_escape')

    def __init__(self):
        self.session = requests.Session()
        self.credentials = Input.get_credentials()
        self.path = Input.get_path()
