import getpass
import re
import requests
from bs4 import BeautifulSoup


class Main():
    @staticmethod
    def get_credentials():
        return {"username": input("Username: "), "password": getpass.getpass("Password: ")}

    @staticmethod
    def get_token(session):
        response = session.get("https://leetcode.com/accounts/login/")
        return BeautifulSoup(response.content, "html.parser").find(attrs={"name": "csrfmiddlewaretoken"})['value']

    @staticmethod
    def login(credentials, token, session):
        session.post("https://leetcode.com/accounts/login/",
                     data={"login": credentials['username']
                         , "password": credentials['password']
                         , "csrfmiddlewaretoken": token},
                     headers={"Content-Type": "application/x-www-form-urlencoded"
                         , "Cookie": "csrftoken=" + token + "; _ga=GA1.2.1164685322.1480633056"
                         , "Referer": "https://leetcode.com/accounts/login/"})

    @staticmethod
    def get_tags(session):
        response = session.get("https://leetcode.com/problemset/algorithms/")
        return list(map(lambda tag: tag['href'], BeautifulSoup(response.content, "html.parser").findAll("a", attrs={
            "href": re.compile(r"/tag/*/")})))

    @staticmethod
    def get_questions(tag, session):
        response = session.get("https://leetcode.com" + tag)
        questions = BeautifulSoup(response.content, "html.parser") \
            .find("table", attrs={"id": "question_list"}).tbody.findAll("tr")
        return list(map(lambda question: question.find("a", attrs={"href": re.compile(r"/problems/*/")})['href'],
                        list(filter(lambda question: question.find("span", attrs={"class": "ac"}) is not None,
                                    questions))))

    @staticmethod
    def get_latest_accepted_submission(submissions):
        return list(filter(lambda submission: submission.strong, submissions))[0]['href']

    @staticmethod
    def get_attribute_value(tag, attribute, next_attribute):
        attribute_value = tag[tag.index(attribute + ": '"):tag.index(next_attribute + ": '")]
        return attribute_value[attribute_value.index("'") + 1:attribute_value.rindex("'")].encode('utf8').decode(
            'unicode_escape')

    @staticmethod
    def save_solution(question, submission, session):
        response = session.get("https://leetcode.com" + submission)
        soup = BeautifulSoup(response.content, "html.parser")
        file_name = soup.find("a", attrs={"href": question}).text
        tag = soup.find("script", text=re.compile(r"submissionCode:*")).text
        code_type = Main.get_attribute_value(tag, "getLangDisplay", "submissionCode");
        code = Main.get_attribute_value(tag, "submissionCode", "editCodeUrl")
        print("Saving solution for '" + file_name + "'")
        with open("../solutions/" + file_name + "." + code_type, 'w') as file_:
            file_.write(code)

    @staticmethod
    def save_solutions(questions, session):
        for question in questions:
            response = session.get("https://leetcode.com" + question + "submissions")
            submissions = BeautifulSoup(response.content, "html.parser").findAll("a", attrs={
                "href": re.compile(r"/submissions/detail/*/")})
            submission = Main.get_latest_accepted_submission(submissions)
            Main.save_solution(question, submission, session)

    @staticmethod
    def process_tags(tags, session):
        for tag in tags:
            print("Saving solutions under '" + tag + "'")
            questions = Main.get_questions(tag, session)
            Main.save_solutions(questions, session)


def main():
    credentials = Main.get_credentials()
    session = requests.Session()
    token = Main.get_token(session)
    Main.login(credentials, token, session)
    tags = Main.get_tags(session)
    Main.process_tags(tags, session)


if __name__ == "__main__":
    main()
