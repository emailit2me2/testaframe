""" So you wanna add a DB object? These instructions should help you get started:
1.First thing first, update your my_config.py file to include the DB keys
    a.Follow the format in my_config.example.py when adding your keys
    b.Update my_config_example.py to include generic data so others can see what other db_objs have been added
2.Next in our_envs.py add the base url to LOCALHOST, STAGING, and PROD in alphabetical order
3.Add Host to env_enums.py
4.Add your DB to std_env.py in alphabetical order
    a.Add creds to the first part of prep_common_databases
5.Add new DB method to db_factory.py
6.Create DB file under the db_objects folder
"""
import traceback

import example_db


class DatabaseFactory(object):
    """Factory for creating database instances."""

    def __init__(self):
        self.generated_databases = []
        self.database_data = {}

    def add_database(self, name, **kwargs):
        self.database_data[name] = kwargs

    def teardown_all(self):
        """Performs a teardown of all databases created by the factory."""
        print "----------Begin Database Teardown----------"
        teardown_success = True

        for db in reversed(self.generated_databases):
            try:
                print "Tearing down: %s VVVVVVVVVVVVV" % repr(db)
                teardown_success = teardown_success and db.teardown()
            except Exception, exc:
                teardown_success = False
                traceback.print_exc()
        print "-----------End Database Teardown-----------"
        assert teardown_success, "Teardown steps within some databases encountered errors. (See above teardown output)"

    def _track_db(self, db):
        print "Creating %s" % repr(db)
        self.generated_databases.append(db)
        return db

    # This method gives the user the ability to overwrite the default our_envs value for the current environment.
    # if the parameter writes_allowed passed into this function is None it will use the default from our_envs
    # however supplying True or False will use those values instead.
    # Ex:
    #       make_example_db(writes_allowed=True)
    def _choose_writes_allowed(self, db_name, writes_allowed=None):
        if writes_allowed is not None:
            return writes_allowed
        else:
            return self.database_data[db_name]["writes_allowed"]

    def make_example_db(self, writes_allowed=True):
        example = example_db.ExampleDb(self.database_data["example"]["creds"],
                              self._choose_writes_allowed("example", writes_allowed))
        return self._track_db(example)


