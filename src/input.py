import getpass


class Input():
    @staticmethod
    def get_credentials():
        return {"username": input("Username: "), "password": getpass.getpass("Password: ")}

    @staticmethod
    def get_path():
        return input("File path: ")
