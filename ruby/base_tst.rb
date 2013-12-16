#!/usr/bin/env ruby

require 'rubygems'
gem 'test-unit'
require 'test/unit'

require 'uri'

require 'base_page'

class TestCaseBase < Test::Unit::TestCase
  class << self
    def startup
      #puts "starting up class"
    end
  end
  def setup
    #puts "starting each test"
    @base_url = 'localhost:8000'
    @driver = Selenium::WebDriver.for :firefox
    @start = PageFactory.new(@driver, @base_url)
  end
  def teardown
    @driver.close
  end
  def try_is_equal(a,b)
    assert_equal(a,b)
  end
end

