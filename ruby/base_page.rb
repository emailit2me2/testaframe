

require 'rubygems'
require 'selenium-webdriver'
require 'uri'

class PageFactory
  attr_reader :driver
  def initialize(driver, base_url)
    @driver = driver
    @base_url = base_url
  end
  def at(page_class, params='', substitutions='')
    new_page = page_class.new(self, params, substitutions)
    @driver.get(new_page.full_url)
    #@log.debug("Goto page #{url}")
    new_page.verify_on_page()
    return new_page
  end
  def on_page(page_class, params='', substitutions='')
    new_page = page_class.new(self, params, substitutions)
    @driver.get(new_page.full_url)
    #@log.debug("On page #{url}")
    new_page.verify_on_page()
    return new_page
  end
end

class ObsoletePage
  def method_missing(m, *args, &block)
    raise NotImplementedError, 'Attempt to use an obsolete page!'
  end
end

class BasePageObj
  TIMEOUT = 10.0
  DELAY = 1.0
  def initialize(factory, params, substitutions)
    @factory = factory
    @driver = @factory.driver
    @params = params
    @substitutions = substitutions
    if not self.class::PAGE_SUB.nil?
      @page = self.class::PAGE_SUB % {:optional_l=>'l'}
    elsif self.respond_to? :PAGE
      @page = self.class:PAGE
    else
      raise NotImplementedError, 'PAGE or PAGE_SUB must be defined per page class'
    end
    if self.respond_to? :PAGE_RE
      @page_re = self.class::PAGE_RE
    else
      @page_re = Regexp.new('^' + @page + '$')
    end
    prep_finders()
  end
  def full_url
    base_url = @factory.base_url   TODO FIXME
    url = "#{base_url}#{@page}#{@params}"
    return url
  end

  def now_on(page_class)
    new_page = @factory.on_page(page_class)
    @driver = ObsoletePage.new()
    return new_page
  end
  def verify_on_page
    path = URI.parse(@driver.current_url).path
    fail "Path to page expected\n#{@page} did not match \n#{path}\n" unless path =~ @page_re
    #p @verify_element
    unless @verify_element
      raise NotImplementedError, "All page objects must have a @verify_element"
    end
    find_the(@verify_element)
  end

  def find_the(element_spec)
    start = Time.now
    while Time.now - start < TIMEOUT
      begin
        puts "find_the #{element_spec}"
        return @driver.find_element element_spec.how => element_spec.spec
      rescue => err
        puts "Delay find_the: #{element_spec} - #{err}"
        #puts err
        sleep(DELAY)
      end
    end
    raise err
  end

  def find_all(element_spec)
    start = Time.now
    while Time.now - start < TIMEOUT
      begin
        puts "find_the #{element_spec}"
        return @driver.find_elements element_spec.how => element_spec.spec
      rescue => err
        puts "Delay find_the: #{element_spec} - #{err}"
        #puts err
        sleep(DELAY)
      end
    end
    raise err
  end

  def click_on(element_spec)
    e = find_the(element_spec)
    e.click()
  end
  def type_into(element_spec, text)
    e = find_the(element_spec)
    e.send_keys(text)
  end
  def submit_form(element_spec)
    e = find_the(element_spec)
    e.submit()
  end

  def method_missing(m, *args, &block)
    p "lookup #{m}"
    sym = ('@'+m.to_s).to_sym
    if instance_variables.include? sym
      ret = instance_variable_get sym
      ret.name = m.to_s
      return ret
    else
      super
    end
  end
  def by_css(locator)
    return ByBase.new(self, :css, locator)
  end
  def by_id(locator)
    return ByBase.new(self, :id, locator)
  end
  def by_name(locator)
    return ByBase.new(self, :name, locator)
  end
  def by_tag_name(locator)
    return ByBase.new(self, :tag_name, locator)
  end
  def by_class_name(locator)
    return ByBase.new(self, :class_name, locator)
  end
  def by_link_text(locator)
    return ByBase.new(self, :link_text, locator)
  end
  def by_partial_link_text(locator)
    return ByBase.new(self, :partial_link_text, locator)
  end
  def by_xpath(locator)
    return ByBase.new(self, :xpath, locator)
  end
end

class ByBase
  attr_reader :how, :spec
  def initialize(page, how, spec)
    @page = page
    @how = how
    @spec = spec
  end
  def name=(my_name)
    @name = my_name
  end
  def to_s
    return @name
  end

  def the_text
    @page.find_the(self).text
    #proc {@page.find_the(self).text }
  end
  def all_the_text
    @page.find_all(self).map {|e| e.text}
  end
  def the_attribute(attrib)
    @page.find_the(self).attribute(attrib)
  end
  def all_the_attributes(attrib)
    @page.find_all(self).map {|e| e.attribute(attrib)}
  end
  def is_this_enabled
    @page.find_the(self).enabled?
  end
  def is_this_displayed
    @page.find_the(self).displayed?
  end
  def length_of
    @page.find_all(self).length
  end

end

