

require 'rubygems'
require 'selenium-webdriver'
require 'uri'

class PageFactory
  def initialize(driver, base_url)
    @driver = driver
    @base_url = base_url
  end
  def at(page_class)
    url_params=""
    url = "#{@base_url}#{page_class::PAGE}#{url_params ? '?' : ''}#{url_params}"
    @driver.get(url)
    #@log.debug("Goto page #{url}")
    return page_class.new(@driver)
  end
end

class BasePageObj
  def initialize(driver)
    @driver = driver
    prep_finders()
    #instance_variables.each{|i| p i}
  end

  def find_the(element_spec)
    return @driver.find_element element_spec.how => element_spec.spec
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

