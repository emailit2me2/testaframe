

require 'rubygems'
require 'selenium-webdriver'
require 'uri'

class PageFactory
  attr_reader :driver
  def initialize(driver, base_url)
    @driver = driver
    @base_url = base_url
  end
  def at(page_class)
    url_params=""
    url = "#{@base_url}#{page_class::PAGE}#{url_params ? '?' : ''}#{url_params}"
    new_page = page_class.new(self)
    @driver.get(url)
    #@log.debug("Goto page #{url}")
    new_page.verify_on_page()
    return new_page
  end
  def on_page(page_class)
    url_params=""
    url = "#{@base_url}#{page_class::PAGE}#{url_params ? '?' : ''}#{url_params}"
    new_page = page_class.new(self)
    @driver.get(url)
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
  def initialize(factory)
    @factory = factory
    @driver = @factory.driver
    prep_finders()
  end

  def now_on(page_class)
    new_page = @factory.on_page(page_class)
    @driver = ObsoletePage.new()
    return new_page
  end
  def verify_on_page
    path = URI.parse(@driver.current_url).path
    fail "Path to page expected\n#{self.class::PAGE} did not match \n#{path}\n" unless self.class::PAGE == path
    #p @verify_element
    unless @verify_element
      raise NotImplementedError, "All page objects must have a @verify_element"
    end
    find_the(@verify_element)
  end

  def find_the(element_spec)
    return @driver.find_element element_spec.how => element_spec.spec
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
    sym = ('@'+m.to_s).to_sym
    if instance_variables.include? sym
      return instance_variable_get sym
    else
      super
    end
  end
  def by_name(locator)
    return ByBase.new(self, :name, locator)
  end
  def by_css(locator)
    return ByBase.new(self, :css, locator)
  end
  def by_link_text(locator)
    return ByBase.new(self, :link_text, locator)
  end
end

class ByBase
  attr_reader :how, :spec
  def initialize(page, how, spec)
    @page = page
    @how = how
    @spec = spec
  end

  def the_text
    return @page.find_the(self).text
  end

end

