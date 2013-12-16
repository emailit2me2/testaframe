
def make_derived(modules, environments, browsers):
  # This combines all the test modules with mixins for selected envs and browsers
  # into derived classes, then passes the resulting string back to run_*.py
  # to be exec'ed into existance so it can be discovered by nose.
  ret = ""
  for module in modules:
    g = module.__name__
    #print dir(module)
    for gg in dir(module):
      if "Test" in gg:
        #print "    Found Test class", gg
        #print gg
        for env in environments:
          for br in browsers:
            # should we put class attr's on these e.g. Ie, Firefox, Chrome, etc?
            e = '''\nclass %s_%s_on_%s_%s(%s.%s, env.%s_EnvMixin, env.%s_SeMixin):\n  pass\n''' % (
                g,br,env,gg, g,gg, env, br)
            #print e
            ret += e
        #
      #
    #
  #
  return ret

# The use of multiple inheritance to provide the env and OS/browser mixins could be
# replaced with a composition style using the following code snippet.
# env.py would need to be reworked to support this but it wouldn't be too hard.
#            e = '''
#class %s_%s_on_%s_%s(%s.%s):
#  def _prep_envs(self):
#    self.env = env.%s_EnvMixin()
#    self.osb = env.%s_SeMixin()
#''' % (
#                g,br,env,gg, g,gg, env, br)
