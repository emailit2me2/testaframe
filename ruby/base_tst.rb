#!/usr/bin/env ruby

require 'rubygems'
gem 'test-unit'
require 'test/unit'

require 'uri'

require 'base_page'

class TestCaseBase < Test::Unit::TestCase
  TIMEOUT = 10.0
  DELAY = 1.0
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
  def try_is_equal(a,b=nil,&blk)
    start = Time.now
    while Time.now - start < TIMEOUT
      begin
        if blk.respond_to? :call
          bval = blk.call
        elsif b.respond_to? :call
          bval = b.call
        else
          bval = b
        end
        raise "  FAIL: #{a} != #{bval}" unless a == bval
        return true
      rescue => err
        puts "Delay #{err}"
        sleep(DELAY)
      end
    end
    raise err
  end
end

