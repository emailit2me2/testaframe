

require 'base_page'

class StdPage < BasePageObj
#  def initialize(driver)
#    prep_finders()
#  end

end


class AjaxyPage < StdPage
  PAGE = "/ajaxy_page.html"
  #attr_reader :new_labels
  def prep_finders
    @new_label_field = by_name 'typer'
    @new_label_form = by_css 'form'
    @new_labels = by_css '.label'
  end
#  def initialize(driver)
#    super(driver)
#    #verify_on_page
#  end
  def fillout_form(new_label)
    type_into(@new_label_field, new_label)
  end
  def submit_fillout_form()
    submit_form(@new_label_form)
  end
#  def new_labels
#    return @new_labels
#  end
end
