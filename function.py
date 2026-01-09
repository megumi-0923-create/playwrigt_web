import csv
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from functools import wraps
import pandas as pd
import string
import time
import logging
import sys


_phrase_cache={}
#通过Unicode编码判断某个字符是否是某个语言的字符
def contains_lang_chars(lang_ranges, text, dictionary=None, test_null=False, latin_letter_ranges=None):
    if dictionary is None:
        dictionary = set()
    dictionary=load_dictionary(dictionary)
    # 专业术语，不进行翻译的内容
    # if latin_letter_ranges is None:
    #     latin_letter_ranges= []
    special_char = []
    char_lst=True
    is_in_dictionary_bool=False
    contains_lang_bool=False
    #将检测内容含有专业术语的部分去除
    for char in special_char:
        if char in text:
            text=text.replace(char,'')
    #去除换行符和制表符
    text = ''.join(c for c in text if c not in ('\n','\t'))
    spe_char = [
        (32, 32),  # 空格
        (48, 57),  # 数字 0-9
        (33, 47),  # ! " # $ % & ' ( ) * + , - . /
        (58, 64),  # : ; < = > ? @
        (91, 96),  # [ \ ] ^ _ `
        (123, 126),  # { | } ~
        (8220, 8221),  # 左双引号 “,右双引号 ”
        (160, 160),  # NO-BREAK SPACE
        (8592, 8594),  # ← → 箭头
        (8730, 8747),  # √ ∫ ∴ 及附近符号
        (8800, 8805),  # ≠ ≥ ≤
        (8721, 8721),  # ∑
        (8719, 8719),  # ∏
        (8734, 8734),  # ∞
        (177, 177),  # ±
        (960, 960),  # π
        (928, 928),  # Π
    ]
    words_list = remove_special_chars(text,spe_char)

    if test_null:
        if text.strip() == '':
            char_lst = False
    if not char_lst:
        return False

    #先检查每个字符是否在给定的Unicode编码里
    for char in text.strip():
        found = False
        code = ord(char)  # 获取一个字符的 Unicode 码值（十进制）
        # 检查这个码值是否没有落在泰语区段内
        for start, end in lang_ranges:
            if start<=code<=end:
                found = True
                contains_lang_bool = True
                break
        for start_spechar, end_spechar in spe_char:
            if start_spechar<=code<=end_spechar:
                found = True
                break
        if latin_letter_ranges is not None:
            for start_basiclatin,end_basiclatin in latin_letter_ranges:
                if start_basiclatin<=code<=end_basiclatin:
                    found=True
        if not found:
            return False

    #如果都在给定的Unicode编码里面，且不包含非拉丁语的字符，再将内容分词，并检测每个单词是否在本地的词典里，只需有1个在词典，就返回True
    if latin_letter_ranges is not None and not contains_lang_bool:
        for word in words_list.split(' '):
            result=is_in_dictionaty(word.lower(),dictionary)
            print(f'待识别的单词:{word.lower()}')
            print(result)
            if result:
                is_in_dictionary_bool=True
                break
        if not is_in_dictionary_bool:
            return False

    # print(text.strip(),text_new)
    return True

#需要做查找字典的时候，将翻译单词缓存到一个字典里面，这样防止后面翻译内容包含这个单词的时候，做重复检测
def contains_lang_cached(unicode_range, text, dictionary=None, test_null=False, latin_letter_ranges=None):
    # 以 text 作为缓存 key（最安全）
    if text in _phrase_cache:
        return _phrase_cache[text]

    result = contains_lang_chars(
        unicode_range,
        text,
        dictionary=dictionary,
        test_null=test_null,
        latin_letter_ranges=latin_letter_ranges
    )

    _phrase_cache[text] = result
    return result

#加载本地词典
def load_dictionary(filelist):
    words=set()
    for file in filelist:
        with open(file, 'r',encoding='utf_8') as f:
            content=f.read()
        for word in content.split():
            word = word.strip(string.punctuation)
            if word and not word.isdigit():
                words.add(word)
    # with open('sssss.txt', 'w',encoding='utf_8') as f:
    #     f.write(str(words))
    return words

#分词判断每个单词是否在本地的词典库
def is_in_dictionaty(word,dictionary:set):
    if word in dictionary:
        return True
    return False

#去除掉给定的text中的那些含有特殊符号，以便后面用来根据空格分词
def remove_special_chars(text, spe_char_ranges):
    result = []
    for char in text:
        code = ord(char)

        # 判断是否是特殊字符
        is_special = any(start <= code <= end for start, end in spe_char_ranges)

        if is_special:
            # 用空格替代
            result.append(' ')
        else:
            result.append(char)

    # 可选：避免返回多重空格（"aaa!!  rrr" → "aaa rrr"）
    cleaned = ' '.join(''.join(result).split())
    return cleaned

#将测试结果写入 测试结果.csv文件
def write_result(filename,rows):
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # writer.writerow(['翻译内容', 'outerHtml', 'result', 'tips'])
        writer.writerows(rows)



#根据输入的根目录元素，搜索该元素下返回的所有含有某个标签的所有元素
def get_th_text(html_element,label):
    # 创建BeautifulSoup解析对象
    soup = BeautifulSoup(html_element, 'html.parser')
    # 查找所有label标签
    tags = soup.find_all(label)
    # 提取每个label的文本内容（包含标签本身）
    list = []
    list_element = []
    for th in tags:
        list.append(th.get_text())
        list_element.append(th)
    return list, list_element

#判断api页面中，图元块的显示是只含有pc，mobile，或是2个都有
def api_button_type(element):
    soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
    tags = soup.find_all('path')
    list = []
    for th in tags:
        list.append(th.get('d'))
    #该图元块只显示了移动端
    if 'M17' in list[0]:
        return 'mobile only'
    #只显示了pc端
    elif len(list)==1:
        return 'pc only'
    else:
        return 'both'

#csv文件中，根据某个字段的值，查询该行另一个字段的值
def search_csv_value(search_value,search_column,target_column,file_path='UGCBlockConfig.csv'):
    df=pd.read_csv(file_path,encoding='utf-8')
    result = df[df[search_column] == search_value]
    return result[target_column]

#UGCBlockConfig中，根据id，查询Division字段的值
def search_csv_column_division(id:str):
    search_column='id'
    target_column='Division'
    value=search_csv_value(id,search_column,target_column)
    return value.iloc[0]

#根据所属division，返回应该有的颜色,返回的是blocklyPath这个class下的fill属性
def api_color(id:str):
    a=str(search_csv_column_division(id)).strip().lower()
    dict={
        'condition':'#205c48',
        'event':'#984848',
        'data':'#984877',
        'action':'#79803b',
        'module':'#326884',
        'function':'#544280'
    }
    for key,value in dict.items():
        if key in a:
            return value
    return -1



#再点击左侧的二级菜单的按钮后，需要判断页面中间的内容是否刷新完成
def content_changed(driver,selectors:dict,old_values:dict):
    for key, xpath in selectors.items():
        try:
            element = driver.find_element(By.XPATH, xpath)
            html = element.get_attribute('outerHTML')
            if html == old_values.get(key):
                return False  # 任意一个没变，说明还没刷新
        except Exception:
            return False
    return True

#本质是点击元素所在的位置；所以如果碰到点击某个按钮后，该按钮位置发生变化的话，需要注意这点
def click_when_ready(page, locator, timeout=7000,double_click=False):
    start = time.time()
    while time.time() - start < timeout / 1000:
        try:
            box = locator.bounding_box()
            if box and locator.is_enabled():  # 元素在页面可见
                if double_click:
                    locator.dblclick()
                    return True
                else:
                    locator.click()
                    return True
        except:
            pass
        time.sleep(0.05)  # 每50ms检查一次
    raise TimeoutError(f"Element {locator} not clickable after {timeout}ms")

#点击三级分类时确保二级列表是展开的
def ensure_second_level_open(page,third_level_a):
    second_li = third_level_a.locator('xpath=ancestor::li[contains(@class,"gfr-catalog-item")][2]')
    ul = second_li.locator('> ul')
    print(f'ul.count:{ul.count()}')
    if ul.count() == 0:
        # 没展开，点 header
        header = second_li.locator('> div > div').nth(0)
        print(second_li.evaluate("el => el.outerHTML"))
        click_when_ready(page, header)
        ul.wait_for(state='attached', timeout=5_000)
        print(f'second_li:{header.inner_text()}')

#记录日志
class PrintToLogger:
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        pass

def logging_init(file,level=logging.INFO):

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    if not logger.handlers:
        file_handler = logging.FileHandler(file, mode="w", encoding="utf-8")
        console_handler = logging.StreamHandler(sys.__stdout__)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

#判断选择器里面的数量是否为0
def checklist_count_is_zero(all_selectors,optional_selectors,page):
    # 验证选择器是否还能找到元素（检测前端代码变更）
    selector_list=[]  # 存储找不到的必需选择器
    for selector in all_selectors:
        count = page.locator(selector).count()
        if count == 0:
            if selector not in optional_selectors:
                # 必需的选择器找不到，添加到列表中
                selector_list.append(selector)
            else:
                # 可选的选择器找不到，只打印调试信息（不添加到列表中）
                print(f'[调试] 可选选择器未找到元素: {selector}（这是正常的）')
        else:
            print(f'[验证] 选择器 {selector} 找到 {count} 个元素')
    
    # 如果有必需选择器找不到，返回列表和False；否则返回空列表和True
    if len(selector_list) > 0:
        return selector_list, False
    else:
        return [], True

