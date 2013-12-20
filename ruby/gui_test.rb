
$:.unshift('.')

require 'rubygems'
gem 'test-unit'

require 'base_tst'
require 'gui_pages'

class TestMyGui < TestCaseBase
  def test_ajaxy
    ajaxy_page = @start.at(AjaxyPage)
    new_label1 = 'new_label1'
    ajaxy_page.fillout_form(new_label1)
    ajaxy_page.submit_fillout_form()
    #sleep(8.0)
    try_is_equal('label') {ajaxy_page.new_labels.the_attribute('class')} # lame example
    try_is_equal(['label'], lambda {ajaxy_page.new_labels.all_the_attributes('class')}) # lame example
    try_is_equal(new_label1,new_label1)
    try_is_equal(new_label1,ajaxy_page.new_labels.the_text)
  end
  def test_next_page
    linked_page = @start.at(LinkedImagePage)
    next_page = linked_page.goto_next_page()
    assert_raise NotImplementedError do
      # because using obsolete page
      linked_page.next_page_link.the_text
    end
  end
  def test_form_page
    # TODO was hoping to get a param in the URL
    form_page = @start.at(FormPage)
    try_is_equal(true, form_page.check_enabled.is_this_enabled)
    try_is_equal(false, form_page.check_disabled.is_this_enabled)
    try_is_equal(true, form_page.check_enabled.is_this_displayed)

    #sleep(2.0)
    next_page = form_page.do_submit()
    try_is_equal(2, next_page.list_items.length_of)
    try_is_equal(['Item 1','Item 2'], next_page.list_items.all_the_text)
  end
  def test_hidden
    hidden_page = @start.at(HiddenPage, {:optional_l=>'l'})
    try_is_equal(false, hidden_page.verify_element.is_this_displayed)
  end
end