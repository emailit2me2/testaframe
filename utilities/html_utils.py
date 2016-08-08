
from bs4 import BeautifulSoup


class HtmlEmailUtils:

    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(self.html)

    def stringify_html(self):
        """Rip all the strings in an HTML email apart and reassemble their lines consistently."""
        a = []
        ss = list(self.soup.stripped_strings)
        #print ss
        for l in ss:
            ll = l.splitlines()
            #print ll
            if len(ll) == 1:
                a.append(l)
            else:  # it had line breaks in it
                a.append(" ".join([lll.strip() for lll in ll]))
        #
        return "\n".join(a)

    def get_links(self):
        """Grab all the links in an HTML email."""
#        print
#        print "\n".join([str(l) for l in self.soup.find_all('a')])
#        print
        return [(link.text, link.get('href')) for link in self.soup.find_all('a')]

