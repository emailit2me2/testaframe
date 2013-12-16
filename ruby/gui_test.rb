
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
    sleep(8.0)
    try_is_equal(new_label1, ajaxy_page.new_labels.the_text)
  end
  def test_next_page
    linked_page = @start.at(LinkedImagePage)
    next_page = linked_page.goto_next_page()
    assert_raise NotImplementedError do
      linked_page.next_page_link.the_text
    end
  end
end