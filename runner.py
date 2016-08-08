
import sys
import glob


def check_no_missing_files(test_dir, module_list, excludes):
    """Ensure no files exist in C{test_dir} that are not imported and included in the C{module_list}
    with the exception of those listed in C{excludes}.

    @param excludes: List of C{package.module} that should not be imported or ecxecuted.
    """
    module_names = set([m.__name__ for m in module_list])
    for module in sorted(glob.glob('%s/*_test.py' % test_dir)):
        pkg_module = test_dir + "." + module.split('/')[-1].split('.')[0]
        assert ((pkg_module in sys.modules.keys()) or
                (pkg_module in excludes)), "Found %s in file system but not imported here" % pkg_module
        assert ((pkg_module in module_names) or
                (pkg_module in excludes)), "Found %s in file system but not in module list" % pkg_module


def debug_print(debug_message):
    pass
    # print debug_message


def make_derived(modules, environments, browsers, count=1, debug=False):
    """This creates all the test modules for selected environments and browsers
       into derived classes, then passes the resulting string back to run_*.py
       to be exec'ed into existance so it can be discovered by nose."""

    # Set aside the pass_count length so we can use that when adding
    # pass_count into the derived class names. minus 1 since 10 passes is 0-9.
    pass_count_length = len(str(count-1))

    class_definitions = "\nimport config.env\n"
    FIELD_SEP = "__"

    # The derived classes don't need any code, they rely on the underlying test module, just replacing
    # environmental & browser details for the provided combinations as constants.
    import_template = "import {curr_module_name}\n"

    # HATE wrapping this way but it's required for PEP8  watch out for the line extender ----V
    class_template = '''
class {curr_module_filename}{FIELD_SEP}{curr_browser}{FIELD_SEP}{curr_environment}{FIELD_SEP}\
{curr_module_member}{pass_number_clause}(
        {curr_module_name}.{curr_module_member}):
    ENV = config.env.{curr_environment}_Env
    OS_BROWSER = config.env.{curr_browser}_OSBrowser
'''

    # Iterate over the given modules.
    for curr_module in modules:

        curr_module_name = curr_module.__name__
        curr_module_filename = curr_module_name.split('.')[-1]  # just grab the file name

        curr_module_members = dir(curr_module)
        debug_print("Module ({curr_module_name}) members: {curr_module_members}".format(**locals()))

        # Iterate the members of each module
        for curr_module_member in curr_module_members:
            debug_print("Found module: {curr_module_member}".format(**locals()))

            # If the member name includes the substring 'Test'
            if "Test" in curr_module_member:
                debug_print("Found Test Class: {curr_module_member}".format(**locals()))
                class_definitions += import_template.format(**locals())

                # Permute environments & browsers within.
                for curr_environment in environments:
                    for curr_browser in browsers:

                        # Make {count} copies of the definition.
                        for pass_number in xrange(count):

                            # Build a pass number clause for the derivative class name when requesting more than one
                            # pass be run.
                            pass_number_clause = ''
                            if count > 1:
                                pass_number_string = str(pass_number).zfill(pass_count_length)
                                pass_number_clause = "{FIELD_SEP}{pass_number_string}".format(**locals())

                            # Generate a new class definition deriving from the current module, but mixing in the
                            # requested environment & browser functionalities.
                            new_definition = class_template.format(**locals())
                            debug_print("Permutation definition: \n{new_definition}".format(**locals()))

                            class_definitions += new_definition

    debug_print("Discovery complete")
    debug_print(class_definitions)
    return class_definitions

# The use of multiple inheritance to provide the env and OS/browser mixins could be
# replaced with a composition style using the following code snippet.
# env.py would need to be reworked to support this but it wouldn't be too hard.
#            e = '''
# class %s_%s_on_%s_%s(%s.%s):
#  def _prep_envs(self):
#    self.env = env.%s_EnvMixin()
#    self.osb = env.%s_SeMixin()
# ''' % (
#                g,br,env,gg, g,gg, env, br)
