class UserView:
    def main_menu(self):
        print(20 * "=", "MAIN MENU", 20 * "=")
        print("1) Register")
        print("2) Log in")
        print("3) Exit")

    def user_menu(self):
        print(20 * "=", "USER MENU", 20 * "=")
        print("1) Send a message")
        print("2) Received messages")
        print("3) Message statistics")
        print("4) Log out")


class AdminView:
    def admin_menu(self):
        print(20 * "=", "ADMIN MENU", 20 * "=")
        print("1) Show all online users")
        print("2) Show N top senders")
        print("3) Show N top spamers")
        print("4) Show last N lines of log")
        print("5) Exit")
