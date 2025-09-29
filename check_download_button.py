from pom.core.driver_factory import create_driver
from pom.pages.login_page import LoginPage
from pom.core.base_page import BasePage
from pom.config import Config

cfg = Config()
d = create_driver(headless=False)
LoginPage(d, cfg).login_with_env()

p = BasePage(d, cfg)

#Download button Options:
x1 = "//*[@id='rc-tabs-0-panel-1']//button[.//svg]"
x2 = "//*[@id='rc-tabs-0-panel-1']//button[.//span[contains(.,'Download')]]"
x3 = "(//*[name()='svg' and contains(@class,'download')]/ancestor::button)[1]"
x4 = "//*[contains(@id,'rc-tabs-') and contains(@id,'-panel-1')]//button[.//svg]"

print("btn has svg:   ", p.exists(x1, 10))
print("btn has text:  ", p.exists(x2, 10))
print("svgbutton:    ", p.exists(x3, 10))
print("panel btn+svg: ", p.exists(x4, 10))

d.quit()
