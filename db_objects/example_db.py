
from enum import unique, Enum

import base_db


class ExampleDb(base_db.BaseDb):

    # Just for example usage at this point.
    @unique
    class EmployeeState(Enum):
        UNKNOWN = 1
        ACTIVE = 2
        ARCHIVED = 3

    EMPLOYEES_DUMP = '''Employees|id|name|state:EmployeeState|@state|$state'''

    def teardown(self):
        # If you created something you should remove it here
        base_db.BaseDb.teardown(self)

    def lookup_state(self, value):
        """Example function.  Sometimes a simple enum lookup isn't enough.
        """
        return self.EmployeeState(value).name
        return self.EmployeeState.reverse_lookup[value]

    def do_state(self, row):
        """Example function.  Sometimes you need to put together different pieces from a whole row.
        """
        return self.EmployeeState(row['state']).name

    def dump_db(self):
        print "----------------- Dumping example DB Stuff -----------------"
        employees = self.get_employees()
        self.dumper(self.EMPLOYEES_DUMP, employees)

    def dump_my_stuff(self):
        """This is designed to take an argument with the items of interest.
        For example if you created Employees in the test then pass the Employee IDs to limit the dump.
        """
        print "----------------- Dumping example DB Stuff -----------------"
        Employees = self.get_employees()
        self.dumper(self.EMPLOYEES_DUMP, Employees)

    def get_employees(self):
        ## limiting to the first 5 since it is only used to show how the dumper works

        sql = '''SELECT * from employees limit 5'''
        return self.query_sql(sql)

#    This is an example of how to do explicit data creation with a databuilder.
#    Pass in the example_db (or vanguard service) to the databuilder
#    In the databuilder have get_uniq_Employee_info() and make_Employee(uniq_Employee_info) functions.
#    def make_Employee_by_hand(self, Employee_info):
#        do SQL statements to create the Employee in the database


if __name__ == '__main__':
    import sys
    import os.path
    # Since we don't have relative imports in python...
    # We need the base directory, so grab the module's location zeroth element,
    # and strip off the module and then mess with the python path... I feel so dirty!!
    sys.path.insert(0,os.path.split(sys.path[0])[0])
    # Only for when it is used as a standalone module for experimentation.
    import config.my_cfg

    example = ExampleDb(config.my_cfg.config['db_creds']['example'])
    example.dump_db()
    example.dump_my_stuff()
