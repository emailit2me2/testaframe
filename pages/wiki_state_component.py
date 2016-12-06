
import base_page
import wiki_pages

class LoginStateComponentBase(base_page.BaseComponent):

    ID = "login_state"

    def _prep_finders(self):
        self.is_logged_in = False


class LoginComponent(LoginStateComponentBase):

    def _prep_finders(self):
        LoginStateComponentBase._prep_finders(self)
        self.login_link = self.by_css('#pt-login a')
        self.verify_component_elements = [self.login_link]
        self.is_logged_in = False

    def goto_login(self):
        self.click_on(self.login_link)
        return self.parent.now_on(wiki_pages.WikiLoginPage)


class LogoutComponent(LoginStateComponentBase):

    def _prep_finders(self):
        LoginStateComponentBase._prep_finders(self)
        self.logout_link = self.by_css('#pt-logout a')
        self.verify_component_elements = [self.logout_link]
        self.is_logged_in = True

    def goto_logout(self):
        self.click_on(self.logout_link)
        return self.parent.now_on(wiki_pages.WikiLogoutPage)


class FauxLoginComponent(LoginComponent):

    def _prep_finders(self):
        LoginComponent._prep_finders(self)

    def verify_component_showing(self):
        pass


class FauxLogoutComponent(LogoutComponent):

    def _prep_finders(self):
        LogoutComponent._prep_finders(self)

    def verify_component_showing(self):
        pass


class LoginStateComponentSelector:
    """Class containing a method handling the logic as to which LoginStateComponent class is being used."""
    @staticmethod
    def get_appropriate_login_component(is_logged_in=False, fake=False):
        if fake:
            if is_logged_in:
                return FauxLogoutComponent
            else:
                return FauxLoginComponent

        if not is_logged_in:
            return LoginComponent

        return LogoutComponent