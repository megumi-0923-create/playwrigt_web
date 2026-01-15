import logging
import unittest
from playwright.sync_api import sync_playwright,expect
from function import *

playwright = sync_playwright().start()
browser = playwright.chromium.launch(
            headless=False,
            slow_mo=50,  # 每个操作延迟50ms，方便观察调试
            args=["--start-maximized", "--disable-extensions"]  # 浏览器启动参数
        )
context = browser.new_context()
page = context.new_page()
page.goto("https://ffcraftland.garena.com/vn/docs/api-11-103/")

# #先点击refereneces
# references_button=page.locator('div.app-docs-tab',has_text='References')
# click_when_ready(page, references_button)
# page.screenshot(path='test1.png',full_page=True)

# #这边发现api列表是默认展开的，所以先把他关上，方便后面写循环
# api_button=page.locator('li.gfr-catalog-item button').nth(0)
# click_when_ready(page, api_button)
# api_button.click()
# print(api_button.evaluate("el => el.outerHTML"))
# page.screenshot(path='test2.png', full_page=True)
#再勾选上obosolete article visible
# locator_obosolete=page.locator('label.com-label.cursor-pointer')
# locator_obosolete_button=locator_obosolete.locator('xpath=./preceding-sibling::button')
# is_checked=locator_obosolete_button.get_attribute('aria-checked')
# print(is_checked)
# if is_checked == 'false':
#     print('aaaaaa')
#     # page.wait_for_timeout(5000)
#     click_when_ready(page, locator_obosolete_button)
#     print('bbbbbb')
#     page.screenshot(path='test2.png',full_page=True)
#
# #再点击api,event分类下，的那些
# for i in range(2):
#     print('======')
#     locator_top=page.locator(f'xpath=//*[@id="__nuxt"]/section/main/section/aside/div/div[4]/div/div/ul/li[{i+1}]')#api和event整个列表
#     #先点击api和event
#     locator_list_title=locator_top.locator('> div > div').nth(0)#api和event本身
#     print(locator_list_title.inner_text())
#     click_when_ready(page, locator_list_title)
#
#     locator_lis_button=locator_top.locator('>ul>li')
#     count=locator_lis_button.count()
#     print(count)
#     for number in range(count):
#         locator=locator_lis_button.nth(number)
#         locator_button=locator.locator('>div>div')
#         click_when_ready(page, locator_button)
#         print(locator_button.inner_text())
utton = locator_third_list.locator('>div>div').nth(0)


# from py_mini_racer import py_mini_racer
#
# ctx = py_mini_racer.MiniRacer()
#
# ctx.eval("""
# function normalizeText(text) {
#     return text.trim().normalize("NFC").toLowerCase()==="đặt thành phần vectơ y";
# }
# """)
#
# text = "Đặt thành phần vectơ y"
# result = ctx.call("normalizeText", text)
#
# print(result)