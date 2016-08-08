

from nose.plugins.attrib import attr
import test_gui.base_tst


@attr('Api')
class WikipediaApiTestBase(test_gui.std_tst.StdApiTestBase):

    def setUp(self):
        test_gui.std_tst.StdApiTestBase.setUp(self)
        self.wikipedia_svc = self.svc_factory.make_wikipedia_svc(self)

    def tearDown(self):
        test_gui.base_tst.TestCaseBase.tearDown(self)


@attr("WikipediaApi")
class TestWikipediaApi(WikipediaApiTestBase):
    """This is an example test of an API.
    An example query result for:
    https://en.wikipedia.org/w/api.php?action=query&titles=Python&format=json
    {
        batchcomplete: "",
        query: {
            pages: {
                46332325: {
                    pageid: 46332325,
                    ns: 0,
                    title: "Python"
                }
            }
        }
    }
    """

    def test_simple_title_query(self):
        title = 'Python'
        result = self.wikipedia_svc.query(titles=title)
        # now pull the data out of the dictionary
        self.is_in(title, [page['title'] for page in self.dict_lookup(result, 'query.pages').values()])


    def test_revisions_title_query(self):
        title = 'Pizza'
        result = self.wikipedia_svc.query(titles=title,prop='revisions',rvprop='content',rvsection='0')
        # now pull the data out of the dictionary
        self.is_in(title, [page['title'] for page in self.dict_lookup(result, 'query.pages').values()])


