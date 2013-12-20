

require 'base_page'

class StdPage < BasePageObj
end


class AjaxyPage < StdPage
  PAGE = "/ajaxy_page.html"
  def prep_finders
    @new_label_field = by_name 'typer'
    @verify_element = @new_label_field
    #@new_label_form = by_css 'form'
    @new_labels = by_css '.label'
  end
  def fillout_form(new_label)
    type_into(@new_label_field, new_label)
  end
  def submit_fillout_form()
    new_label_form = by_css 'form'
    submit_form(new_label_form)
  end
end

class LinkedImagePage < StdPage
  PAGE = '/linked_image.html'
  NEXT_PAGE_LINK_TEXT = 'Click here for next page'
  def prep_finders
    @next_page_link = by_link_text NEXT_PAGE_LINK_TEXT
    @verify_element = @next_page_link
  end
  def goto_next_page
    click_on(@next_page_link)
    now_on(ResultPage)
  end
end

class ResultPage < StdPage
  PAGE = '/resultPage.html'
  def prep_finders
    @verify_element = by_css '#greeting'
    @list_items = by_css 'li'
  end
end

class FormPage < StdPage
  PAGE = '/formPage.html'
  def prep_finders
    @verify_element = by_css '#nested_form input'
    @check_enabled = by_css '#checky'
    @check_disabled = by_css '#disabledchecky'
  end
  def do_submit
    click_on(@verify_element)
    now_on(ResultPage)
  end
end
class HiddenPage < StdPage
  PAGE_RE = '/hidden.html?'
  PAGE_SUB = "/hidden.htm%{optional_l}"
  def prep_finders
    @verify_element = by_css '#singleHidden'
  end
end

