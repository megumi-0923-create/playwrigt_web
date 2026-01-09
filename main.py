import logging
import unittest
import re
from playwright.sync_api import sync_playwright,expect
from urllib.parse import urlparse
from sympy import evaluate
from urllib.parse import urlparse

from function import *


#不同语言下，obsolete这个单词应该翻译的内容，用于后面判断该api是否是废弃的
obsolete_lang_dict={
    'en':'obsolete',
    'th':'เก่า',
    'ar':'قديم'
}


class baselangdetect(unittest.TestCase):
    result_rows=[]
    result_file = None
    lang=None
    unicode_range = None
    dictionary = None
    latin_letter_ranges=None
    # 类变量：用于跟踪 Playwright 和 Browser 是否已经启动（所有子类共享）
    _playwright_instance = None
    _browser_instance = None
    
    @classmethod
    def setUpClass(cls):
        # 如果 Playwright 还没有启动，则启动它（所有测试类共享）
        if baselangdetect._playwright_instance is None:
            baselangdetect._playwright_instance = sync_playwright().start()
            baselangdetect._browser_instance = baselangdetect._playwright_instance.chromium.launch(
                headless=True,
                slow_mo=50,  # 每个操作延迟50ms，方便观察调试
                args=["--start-maximized"]  # 浏览器启动参数
            )
        
        # 每个测试类使用共享的 browser，但创建自己的 context 和 page
        cls.playwright = baselangdetect._playwright_instance
        cls.browser = baselangdetect._browser_instance
        cls.context = cls.browser.new_context(
            viewport=None
        )
        cls.page = cls.context.new_page()
        cls.page.goto(f"https://ffcraftland.garena.com/{cls.lang}/docs/api/")
        # cls.page.locator('.app-docs-inner/section.flex').wait_for(state='visible')  # 等待中间那些东西显示
        cls.result_rows=[]



    @classmethod
    def tearDownClass(cls):
        if cls.result_file is not None:
            write_result(cls.result_file,cls.result_rows)
        else:
            logging.info("No result file")
        # 只关闭当前测试类的 context（会自动关闭 page），不要关闭共享的 browsertearDownClass
        if hasattr(cls, 'context') and cls.context:
            cls.context.close()

    def setUp(self):
        # 在每个测试开始时，将测试名称添加到 result_rows
        self.__class__.result_rows.append([self._testMethodName, '', '', ''])
        self.page=self.__class__.page
        self.unicode_range=self.__class__.unicode_range

    def tearDown(self):
        self.__class__.result_rows.append(['', '', '', ''])

    def test_01_top_menu(self):# 测试页面上方home,tutorial等menu页,测试内容:'测试内容展示/1.png'
        page=self.page
        unicode_range=self.unicode_range
        current_url = page.url  # 获取当前页面URL
        gfr_menu_list=page.locator('ul.gfr-menu-list')
        text=gfr_menu_list.nth(0).inner_text()
        outer_html = gfr_menu_list.nth(0).evaluate("el => el.outerHTML")
        # print(gfr_menu_list.nth(0).inner_text())
        # print(outer_html)
        result=contains_lang_cached(unicode_range,text,dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
        if not result:
            self.__class__.result_rows.append([text,outer_html,result,current_url])

    def test_02_left_menu(self):#测试左侧菜单栏的文字
        page=self.page
        unicode_range=self.unicode_range
        #搜索栏的filter by title
        locator_filterbytitle=page.locator('input.app-docs-filter-input')
        locator_filterbytitle_text=locator_filterbytitle.get_attribute('placeholder')
        result=contains_lang_cached(unicode_range,locator_filterbytitle_text,dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
        outerhtml_filter=locator_filterbytitle.evaluate("el => el.outerHTML")
        current_url = page.url
        if not result:
            self.__class__.result_rows.append([locator_filterbytitle_text,outerhtml_filter,result,current_url])

        #搜索栏下面的obosolete article visible
        locator_obosolete=page.locator('label.com-label.cursor-pointer')
        locator_obosolete_text=locator_obosolete.inner_text()
        outerhtml_obosolete=locator_obosolete.evaluate("el => el.outerHTML")
        current_url = page.url
        result=contains_lang_cached(unicode_range,locator_obosolete_text,dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
        if not result:
            self.__class__.result_rows.append([locator_obosolete_text, outerhtml_obosolete, result,current_url])

        #obosolete article visible选项下的modules和references
        locator_module_reference=page.locator('div.app-docs-tab')
        count=locator_module_reference.count()
        for i in range(count):
            locator=locator_module_reference.nth(i)
            text=locator.inner_text()
            outerhtml=locator.evaluate("el => el.outerHTML")
            result=contains_lang_cached(unicode_range,text,dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
            current_url = page.url
            if not result:
                self.__class__.result_rows.append([text,outerhtml,result,current_url])


    #测试modules下的所有分类，测试内容:'测试内容展示/2.png'
    def test_03_modules_menu(self):
        page = self.page
        unicode_range = self.unicode_range
        modules_tab = page.locator("div.app-docs-tab").nth(0)
        click_when_ready(page, modules_tab)

        #modules分类下的所有
        locator_modules_tab=page.locator('ul.gfr-catalog li a')
        count=locator_modules_tab.count()
        for i in range(count):
            locator=locator_modules_tab.nth(i)
            text=locator.inner_text()
            outerhtml=locator.evaluate("el => el.outerHTML")
            result=contains_lang_cached(unicode_range,text,dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
            current_url = page.url
            if not result:
                self.__class__.result_rows.append([text,outerhtml,result,current_url])

    #测试enum页面,enum页面右边的index页不显示内容
    def test_04_enum(self):
        page=self.page
        unicode_range = self.unicode_range
        #点击enum选项
        locator_enum_top=page.locator('xpath=//*[@id="__nuxt"]/section/main/section/aside/div/div[4]/div/div/ul/li[4]')
        locator_enum_top_button=locator_enum_top.locator('>div>div').nth(0)
        click_when_ready(page, locator_enum_top_button,double_click=True)

        page.wait_for_selector(
            'article.app-markdown-content h1',
            state='visible',
            timeout=10_000
        )

        checklist_list = [
            '.app-docs-nav-index',  # 右侧的index
            'a.app-doc-nav-link',  # 右侧的index下的子分类
            'nav.breadcrumb-container .breadcrumb-text',  # 中间内容，最上方的导航页
            'h1.app-docs-title',  # 整个页面的大标题
            'footer.app-markdown-footer span.app-markdown-line-title.app-markdown-line-title--desktop',  # 页面底下的上一页/下一页

            # '测试内容展示/6.png',有的页面这边没有，底下会返回空，不影响测试
            'div.app-markdown-ctx h1',
            'div.app-markdown-ctx h2',
            'div.app-markdown-ctx h3',
            'div.app-markdown-ctx p',
            'div.app-markdown-table th',
            'div.app-markdown-table td',
            'div.inline-flex.flex-wrap a.gfr-tag',
            'div.inline-flex.flex-wrap div.gfr-tooltip-content'
        ]

        texts = page.locator(','.join(checklist_list)).evaluate_all(
            """
                els => els.map(el => ({
                    text: el.textContent ? el.textContent.trim() : '',
                    html: el.outerHTML
                }))
                .filter(item => item.text.length > 0)
            """)
        current_url = page.url
        for text in texts:
            result = contains_lang_cached(unicode_range, text['text'],dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
            if not result:
                self.__class__.result_rows.append([text['text'], text['html'], result, current_url])
            # print(text['text'])

    # 测试references下的所有分类
    def test_05_references_menu(self):
        page = self.page
        unicode_range = self.unicode_range
        lang=self.lang

        # 先点击refereneces
        references_button = page.locator('div.app-docs-tab').nth(1)
        print(f'references_button_text:{references_button.inner_text()}')
        click_when_ready(page, references_button)
        # page.screenshot(path='test1.png', full_page=True)

        # 再勾选上obosolete article visible
        locator_obosolete = page.locator('label.com-label.cursor-pointer')
        locator_obosolete_button = locator_obosolete.locator('xpath=./preceding-sibling::button')
        is_checked = locator_obosolete_button.get_attribute('aria-checked')
        # print(is_checked)
        if is_checked == 'false':
            print('obosolete需要勾选上')
            page.wait_for_timeout(5000)
            click_when_ready(page, locator_obosolete_button)
            # page.screenshot(path='test2.png', full_page=True)

        # 点击1级
        need_third_click=True
        for i in range(3):
            # print('======')
            locator_top = page.locator(f'xpath=//*[@id="__nuxt"]/section/main/section/aside/div/div[4]/div/div/ul/li[{i + 1}]')  # api和event整个列表
            # 先点击api和event
            locator_list_title = locator_top.locator('> div > div').nth(0)  # api和event本身
            # print(locator_list_title.inner_text())
            click_when_ready(page, locator_list_title)

            locator_lis_button = locator_top.locator('>ul>li')
            second_list_count = locator_lis_button.count()
            if i==2:
                need_third_click=False
            print(f'second_list_count:{second_list_count}')
            # print(count)
            for number in range(second_list_count):
                print(f'====================二级：{number}======================')
                # page.wait_for_timeout(5000)
                locator = locator_lis_button.nth(number)
                locator_button = locator.locator('>div>div')
                click_when_ready(page, locator_button)
                page.wait_for_timeout(5000)
                print(f'{page.locator("h1.app-docs-title").inner_text()}')

                current_href=page.url
                third_lists=locator.locator('>ul>li')
                third_lists_number=third_lists.count()
                print(f'third_lists_number:{third_lists_number}')

                if need_third_click:
                    for index in range(third_lists_number):
                        print('==============================================')
                        print(f'number:{number}, index:{index}')

                        locator_third_list = third_lists.nth(index)

                        button = locator_third_list.locator('>div>div').nth(0)
                        href = button.locator('>a').get_attribute('href')
                        expected_title = button.inner_text().strip()
                        expected_title_norm = expected_title.lower()
                        print(f'href:{href}')
                        print(f'expected_title:{expected_title}')

                        if href == f'/{lang}/docs/api-1-990/':
                            continue
                        target_path = href

                        current_path = urlparse(page.url).path

                        # 点击前调试：验证按钮实际对应的链接
                        a_tag = None  # 初始化为 None，避免未定义错误
                        try:
                            # 尝试多种方式获取链接，确保一致性
                            a_tag = button.locator('>a').first
                            href_from_a = a_tag.get_attribute('href')
                            href_from_button_direct = third_lists.nth(index).locator('>div>div>a').get_attribute('href')

                            print(f'[点击前] 当前URL: {page.url}')
                            print(f'[点击前] 当前path: {current_path}')
                            print(f'[点击前] href(button方式): {href}')
                            print(f'[点击前] href(a标签方式): {href_from_a}')
                            print(f'[点击前] href(直接定位): {href_from_button_direct}')

                            # 如果 href 不一致，使用 a 标签的直接值
                            if href != href_from_a:
                                print(f'[警告] href不一致！使用a标签的值: {href_from_a}')
                                href = href_from_a
                                target_path = href
                        except Exception as debug_e:
                            print(f'[调试] 获取a标签时出错: {debug_e}，将使用button作为fallback')
                            # a_tag 保持为 None，后续会使用 button 作为 fallback

                        if current_path != target_path:
                            old_html = page.locator('section.app-docs-content[data-show="true"]').inner_html()

                            # 直接点击 <a> 标签（如果存在），否则点击 button，确保导航正确
                            click_target = a_tag if a_tag is not None else button
                            print(f'[点击] 准备点击，目标path: {target_path}, 使用{"a_tag" if a_tag is not None else "button"}')
                            click_when_ready(page, click_target)

                            # 等待一小段时间，观察 URL 是否开始变化
                            page.wait_for_timeout(100)
                            immediate_path = page.evaluate("() => window.location.pathname")
                            print(f'[点击后100ms] 当前path: {immediate_path}')

                            # 等 URL 切到目标 path
                            try:
                                page.wait_for_function(
                                    """(targetPath) => window.location.pathname === targetPath""",
                                    arg=target_path,
                                    timeout=15_000
                                )
                                print(f'[成功] URL已跳转到: {target_path}')
                            except Exception:
                                final_path = page.evaluate("() => window.location.pathname")
                                print(f"[timeout] 点击后最终pathname = {final_path}")
                                print(f"[timeout] 期望的target path = {target_path}")
                                print(f"[timeout] 点击前的path = {current_path}")
                                # 检查是否有其他链接被点击了
                                all_links = page.evaluate("""() => {
                                    const links = Array.from(document.querySelectorAll('section.app-docs-content[data-show="true"] a[href*="/docs/api-"]'));
                                    return links.map(a => a.href);
                                }""")
                                print(f"[调试] 页面中所有api链接: {all_links[:5]}")  # 只打印前5个
                                raise

                            # 再等内容区真正变化
                            page.wait_for_function(
                                """(oldHtml) => {
                                    const el = document.querySelector('section.app-docs-content[data-show="true"]');
                                    return el && el.innerHTML !== oldHtml;
                                }""",
                                arg=old_html,
                                timeout=15_000
                            )

                        page.wait_for_selector(
                            'section.app-docs-content[data-show="true"] article.app-markdown-content',
                            timeout=15_000
                        )
                        page.wait_for_selector(
                            'section.app-docs-content[data-show="true"] h1.app-docs-title',
                            timeout=15_000
                        )

                        # 确认标题已经变成当前 3 级菜单的标题
                        try:
                            page.wait_for_function(
                                """(expected) => {
                                    const h1 = document.querySelector('section.app-docs-content[data-show="true"] h1.app-docs-title');
                                    if (!h1) return false;
                                    const text = h1.textContent.trim().toLowerCase();
                                    return text === expected;
                                }""",
                                arg=expected_title_norm,
                                timeout=10_000
                            )
                        except Exception:
                            actual_title = page.locator('h1.app-docs-title').text_content()
                            print(f'[debug] wait title timeout, expected(lower):{expected_title_norm}, actual:{actual_title}')
                            raise

                        print(f'page.url:{page.url}')

                        current_title = page.locator('h1.app-docs-title').evaluate("el => el.textContent.trim()")
                        print(f'current_title:{current_title}')

                        blockly = page.locator(
                            'section.app-docs-content[data-show="true"] div.app-markdown-blockly'
                        )
                        has_blockly = blockly.count() > 0
                        print(f'has_blockly:{has_blockly}')

                        if has_blockly:
                            blockly.wait_for(state='attached', timeout=10_000)

                            # svg 可能初始不可见，这里只要挂载即可
                            page.wait_for_selector(
                                'section.app-docs-content[data-show="true"] '
                                'div.app-markdown-blockly svg',
                                state='attached',
                                timeout=10_000
                            )
                            # 确认 blockly svg 有实际尺寸
                            page.wait_for_function(
                                """() => {
                                    const svg = document.querySelector('section.app-docs-content[data-show="true"] div.app-markdown-blockly svg.blocklySvg');
                                    if (!svg) return false;
                                    const { width, height } = svg.getBoundingClientRect();
                                    return width > 0 && height > 0;
                                }""",
                                timeout=10_000
                            )
                            # 等 blocklyPath 挂载且非空尺寸
                            page.wait_for_selector(
                                'section.app-docs-content[data-show="true"] '
                                'div.app-markdown-blockly path.blocklyPath',
                                state='attached',
                                timeout=15_000
                            )
                            page.wait_for_function(
                                """() => {
                                    const path = document.querySelector('section.app-docs-content[data-show="true"] div.app-markdown-blockly path.blocklyPath');
                                    if (!path) return false;
                                    const box = path.getBBox();
                                    return box && box.width > 0 && box.height > 0;
                                }""",
                                timeout=10_000
                            )

                        # 获取这个按钮的文字，后面要判断是否含有 obsolete
                        text_obsolete = button.inner_text()

                        # page.screenshot(path=f'test_{i}.png',full_page=True)
                        # 需要测试的内容
                        checklist_list = [
                            '.app-docs-nav-index',  # 右侧的index
                            'a.app-doc-nav-link',  # 右侧的index下的子分类
                            'nav.breadcrumb-container .breadcrumb-text',  # 中间内容，最上方的导航页
                            'nav.breadcrumb-container .breadcrumb-link',  # 中间内容，最上方的导航页
                            'h1.app-docs-title',  # 整个页面的大标题
                            'p.app-docs-brief',  # 图片:'测试内容展示/5.png'
                            'footer.app-markdown-footer span.app-markdown-line-title.app-markdown-line-title--desktop',  # 页面底下的上一页/下一页

                        ]

                        # 允许为空的选择器（某些页面可能没有这些元素，这是正常的）
                        optional_selectors = {
                            'p.app-docs-brief',
                            'div.app-markdown-ctx h1',
                            'div.app-markdown-ctx h2',
                            'div.app-markdown-table th',
                            'div.app-markdown-table td',
                        }
                        all_selectors = list(checklist_list)
                        for opt_selector in optional_selectors:
                            if opt_selector not in all_selectors:
                                all_selectors.append(opt_selector)
                        selector_list,count_is_zero=checklist_count_is_zero(all_selectors,optional_selectors,page)

                        if not count_is_zero:
                            warning_msg = f'[选择器失效] href:{href}, 选择器未找到元素: {selector_list}'
                            print(warning_msg)
                            logging.warning(warning_msg)

                        texts = page.locator(','.join(all_selectors)).evaluate_all(
                            """
                                els => els.map(el => ({
                                    text: el.textContent ? el.textContent.trim() : '',
                                    html: el.outerHTML
                                }))
                                .filter(item => item.text.length > 0)
                            """)
                        for text in texts:
                            result = contains_lang_cached(unicode_range, text['text'],dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
                            if not result:
                                self.__class__.result_rows.append([text['text'], text['html'], result, page.url])
                            # print(text['text'])
                        if has_blockly:
                            #检测中间图元块的颜色
                            button_pc=page.locator('button svg path[d^="M20"]')
                            if button_pc.count()==0:
                                print(f'没有pc切换按钮:{href}')
                                self.__class__.result_rows.append([href,'图元块中，没有切换pc按钮', False, ''])
                                continue

                            # 先检查渲染器是否存在
                            renderer_locator = page.locator('div.app-markdown-blockly div.eca_renderer-renderer')
                            if renderer_locator.count() == 0:
                                print(f'[警告] 页面 {href} 没有找到渲染器，跳过 PC 按钮点击')
                                self.__class__.result_rows.append([href,'没有找到渲染器', False, ''])
                                continue

                            old_html_blockly = renderer_locator.inner_html()
                            click_when_ready(page, button_pc, double_click=True)
                            page.wait_for_selector('div.app-markdown-blockly div.eca_renderer-renderer', timeout=10_000)

                            # 等待 innerHTML 变化，如果超时则检查渲染器是否正常，然后继续
                            try:
                                page.wait_for_function(
                                    """(oldHtml) => {
                                        const el = document.querySelector('div.app-markdown-blockly div.eca_renderer-renderer');
                                        if (!el) return false;
                                        return el.innerHTML !== oldHtml;
                                    }""",
                                    arg=old_html_blockly,
                                    timeout=15_000
                                )
                            except Exception as e:
                                # 超时或出错时，打印调试信息，但尝试继续执行
                                try:
                                    current_html = renderer_locator.inner_html()
                                    # 检查至少渲染器还在，并且有 path.blocklyPath，说明渲染正常
                                    has_path = page.locator('div.app-markdown-blockly path.blocklyPath').count() > 0
                                    print(f'[警告] href:{href} - PC按钮点击后innerHTML未变化，但渲染器存在')
                                    print(f'[调试] old_html长度:{len(old_html_blockly)}, current_html长度:{len(current_html)}')
                                    print(f'[调试] html是否相同:{old_html_blockly == current_html}')
                                    print(f'[调试] path.blocklyPath存在:{has_path}')
                                    if not has_path:
                                        print(f'[严重] href:{href} - 渲染器存在但没有path.blocklyPath，可能渲染失败')
                                        self.__class__.result_rows.append([href,'PC切换后blocklyPath不存在', False, ''])
                                        continue
                                except Exception as debug_e:
                                    print(f'[调试] href:{href}, 无法获取当前HTML状态: {debug_e}')
                                # 继续执行，不中断测试（假设渲染已经完成）


                            # 匹配最后一个 - 后面的数字
                            match = re.search(r'-([0-9]+)(?=/)', href)
                            id=match.group(1)
                            color=page.locator('path.blocklyPath').nth(0).get_attribute('fill')
                            result = color == '#48484d' if obsolete_lang_dict[lang] in text_obsolete.lower() else color == api_color(id)
                            if not result:
                                self.__class__.result_rows.append([href,'颜色错了', result, f'现在的颜色是:{color}'])
                            print(f'color测试的:{color},result:{result}')


                # page.wait_for_timeout(500)
                # print(locator_button.inner_text())

        # 点击type
        locator_top_type = page.locator(f'xpath=//*[@id="__nuxt"]/section/main/section/aside/div/div[4]/div/div/ul/li[3]')
        locator_type_title = locator_top_type.locator('> div > div').nth(0)
        click_when_ready(page, locator_type_title)
        page.wait_for_timeout(1000)

        # 然后对所有左侧的条目，进行检测
        locator_items = page.locator('div.gfr-catalog-item-title.capitalize')
        count = locator_items.count()
        for i in range(count):
            locator_items_text = locator_items.nth(i).inner_text()
            # print('=======')
            # print(locator_items_text)
            outerhtml = locator_items.nth(i).evaluate("el => el.outerHTML")
            result = contains_lang_cached(unicode_range, locator_items_text,dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
            if not result:
                self.__class__.result_rows.append([locator_items_text, outerhtml, result, ''])




    #             page.reload()
    #             # 等待按钮重新加载
    #             page.wait_for_selector(f'div.gfr-catalog-item-title.capitalize a{exclude_selector}', timeout=10_000)

    #api,event,type这三个页面的内容
    def test_06_api_self(self):
        lang=self.lang
        page=self.page
        unicode_range = self.unicode_range

        for number in range(1,4,1):
            print('=======')
            old_html = page.locator('div.app-markdown-ctx').nth(0).inner_html()

            locator_top=page.locator(f'//*[@id="__nuxt"]/section/main/section/aside/div/div[4]/div/div/ul/li[{number}]')
            button=locator_top.locator('>div>div').nth(0)
            click_when_ready(page, button, double_click=False)
            page.wait_for_selector('section.app-docs-content[data-show="true"]',timeout=10_000)
            page.wait_for_selector('div.app-markdown-ctx', timeout=10_000)

            page.wait_for_function(
                """({ oldHtml }) => {
                    const el = document.querySelector('div.app-markdown-ctx')
                    return el && el.innerHTML !== oldHtml
                }""",
                arg={
                    "oldHtml": old_html
                },
                timeout=10_000
            )
            checklist_list = [
                '.app-docs-nav-index',  # 右侧的index
                'a.app-doc-nav-link',  # 右侧的index下的子分类
                'nav.breadcrumb-container .breadcrumb-text',  # 中间内容，最上方的导航页
                'h1.app-docs-title',  # 整个页面的大标题
                'footer.app-markdown-footer span.app-markdown-line-title.app-markdown-line-title--desktop',  # 页面底下的上一页/下一页

                # '测试内容展示/6.png',有的页面这边没有，底下会返回空，不影响测试
                'div.app-markdown-ctx h1',
                'div.app-markdown-ctx h2',
                'div.app-markdown-ctx p',
            ]

            optional_selectors=[
                # '测试内容展示/6.png',有的页面这边没有，底下会返回空，不影响测试
                'div.app-markdown-ctx h1',
                'div.app-markdown-ctx h2',
                'div.app-markdown-ctx p',
            ]
            all_selectors = list(checklist_list)
            for opt_selector in optional_selectors:
                if opt_selector not in all_selectors:
                    all_selectors.append(opt_selector)
            selector_list, count_is_zero = checklist_count_is_zero(all_selectors, optional_selectors, page)

            if not count_is_zero:
                warning_msg = f'[选择器失效] href:{page.url}, 选择器未找到元素: {selector_list}'
                print(warning_msg)
                logging.warning(warning_msg)

            texts = page.locator(','.join(checklist_list)).evaluate_all(
                """
                    els => els.map(el => ({
                        text: el.textContent ? el.textContent.trim() : '',
                        html: el.outerHTML
                    }))
                    .filter(item => item.text.length > 0)
                """)
            for text in texts:
                result = contains_lang_cached(unicode_range, text['text'],dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
                if not result:
                    self.__class__.result_rows.append([text['text'], text['html'], result, page.url])
                # print(text['text'])

    #modules分类下，页面的内容
    def test_07_modules(self):
        lang=self.lang
        page=self.page
        unicode_range = self.unicode_range

        old_lists_number=page.locator('li.gfr-catalog-item').count()
        #点击modules按钮
        button_modules=page.locator('div.app-docs-tab').nth(0)
        click_when_ready(page, button_modules, double_click=True)

        page.wait_for_function(
            """({old_lists_number}) => {
                const el = document.querySelectorAll('li.gfr-catalog-item')
                return el && el.length !== old_lists_number
            }""",
            arg={
                'old_lists_number':old_lists_number
            },
            timeout=10_000

        )
        count=page.locator('div.gfr-catalog-item-title.capitalize').count()
        for i in range(count):
            old_html =page.locator('section.app-docs-header').inner_html()

            button=page.locator('div.gfr-catalog-item-title.capitalize').nth(i)
            print('==========')
            print(button.inner_text())
            click_when_ready(page, button, double_click=False)
            page.wait_for_function(
                """({old_html}) => {
                                const el = document.querySelectorAll('section.app-docs-header')
                                return el && el.innerHTML !== old_html
                            }""",
                arg={
                    'old_html': old_html
                },
                timeout=10_000
            )
            checklist_list = [
                '.app-docs-nav-index',  # 右侧的index
                'a.app-doc-nav-link',  # 右侧的index下的子分类
                'nav.breadcrumb-container .breadcrumb-text',  # 中间内容，最上方的导航页
                'h1.app-docs-title',  # 整个页面的大标题
                'footer.app-markdown-footer span.app-markdown-line-title.app-markdown-line-title--desktop',  # 页面底下的上一页/下一页
                'div.gfr-tooltip a',# required module
                'div.gfr-tooltip-content',#required module下面的提示

                # '测试内容展示/6.png',有的页面这边没有，底下会返回空，不影响测试
                'div.app-markdown-ctx h1',
                'div.app-markdown-ctx p',
                'div.app-markdown-ctx th',
                'div.app-markdown-ctx td'

            ]

            optional_selectors = [
                # '测试内容展示/6.png',有的页面这边没有，底下会返回空，不影响测试
                'div.app-markdown-ctx h1',
                'div.app-markdown-ctx h2',
                'div.app-markdown-ctx p',
            ]
            all_selectors = list(checklist_list)
            for opt_selector in optional_selectors:
                if opt_selector not in all_selectors:
                    all_selectors.append(opt_selector)
            selector_list, count_is_zero = checklist_count_is_zero(all_selectors, optional_selectors, page)

            if not count_is_zero:
                warning_msg = f'[选择器失效] href:{page.url}, 选择器未找到元素: {selector_list}'
                print(warning_msg)
                logging.warning(warning_msg)

            texts = page.locator(','.join(checklist_list)).evaluate_all(
                """
                    els => els.map(el => ({
                        text: el.textContent ? el.textContent.trim() : '',
                        html: el.outerHTML
                    }))
                    .filter(item => item.text.length > 0)
                """)
            for text in texts:
                result = contains_lang_cached(unicode_range, text['text'],dictionary=self.__class__.dictionary,latin_letter_ranges=self.__class__.latin_letter_ranges)
                if not result:
                    self.__class__.result_rows.append([text['text'], text['html'], result, page.url])