
import pymysql
import pymysql.cursors


class BaseDb:

    SUCCESSFUL_TEARDOWN = True
    ERRORS_IN_TEARDOWN = False

    def __init__(self, info, writes_allowed=True):
        assert info, "Credentials required for: %s" % self
        self.info = info
        self.info.update({'cursorclass': pymysql.cursors.DictCursor})
        self.writes_allowed = writes_allowed
        self._prep()

    def __str__(self):
        return "{self.__class__.__name__}".format(**locals())
    def __repr__(self):
        return "{self.__class__.__name__} for {self.info[user]}@{self.info[host]} on {self.info[db]}".format(**locals())

    def teardown(self):
        if self.db:
            self.close()
        return self.SUCCESSFUL_TEARDOWN

    def _prep(self):
        self.db = None

    def lazy_connect(self):
        if not self.db:
            self.db = pymysql.connect(**self.info)
            self.db.autocommit(True)

    def close(self):
        self.db.close()
        self._prep()

    def execute_sql(self, sql):
        self.lazy_connect()
        # print sql
        cur = self.db.cursor()
        cur.execute(sql)
        # self.db.commit()  # using autocommit instead
        # cur.close()

    def query_sql(self, sql, *args):
        self.lazy_connect()
        # print sql
        cur = self.db.cursor()
        cur.execute(sql, args)
        ret = cur.fetchall()
        # import pprint
        # pprint.pprint(ret)
        return ret
        # self.db.commit()  # using autocommit instead
        # cur.close()

    def dumper(self, format, result):
        title,ret = self.dump_formatter(format, result)
        print("%s: %d" % (title, len(ret)))
        #print "%d: %s" % (len(ret), format)
        for res in ret:
            print("  %s" % res)

    def dump_formatter(self, format, result):
        ret = []
        fields = format.split('|')
        title = fields.pop(0)
        for row in result:
            ret2 = []
            for field in fields:
                if ':' in field:
                    pieces = field.split(':')
                    val = getattr(self, pieces[1])(row[pieces[0]]).name
                    ret2.append(val)
                elif field.startswith('@'):
                    val = getattr(self, "lookup_%s"%(field[1:],))(row[field[1:]])
                    ret2.append(val)
                elif field.startswith('$'):
                    val = getattr(self, "do_%s"%(field[1:],))(row)
                    ret2.append(val)
                else:  # just a field
                    ret2.append(str(row[field]))
            ret.append("|".join(ret2))
        return title,ret



