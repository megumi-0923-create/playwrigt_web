import os

from datetime import datetime
from main import *

#en，简中，繁中，没有进行测试
LANG_CONFIG = {
    "th":
    {
        "unicode_ranges": [(0x0E00, 0x0E7F), (0x0E80, 0x0EAF), (0x0EB0, 0x0ED5)],
        "dictionary": None,
        'latin_letter_ranges':None
    },
    "ar":
    {
        "unicode_ranges": [
            (0x0600, 0x06FF),
            (0x0750, 0x077F),
            (0x08A0, 0x08FF),
            (0xFB50, 0xFDFF),
            (0xFE70, 0xFEFF),
            (0x1EE00, 0x1EEFF),
        ],
        "dictionary": None,
        'latin_letter_ranges':None
    },
    "ind":{
        "unicode_ranges": [(0x0041, 0x007A)],
        "dictionary": None,
        'latin_letter_ranges':None
    },
    "es":{
        "unicode_ranges": [(0x00C0, 0x00FF)],
        "dictionary": ['dictionary/spanish_dictionart_txt/es_full.txt'],
        'latin_letter_ranges':[(0x0041, 0x007A)]
    },
    "pt-br":{
        "unicode_ranges": [(0x00C0, 0x00FF)],
        "dictionary": ['dictionary/portuguese_dictionary_txt/pt_full.txt'],
        'latin_letter_ranges':[(0x0041, 0x007A)]
    },
    "vn":{
        "unicode_ranges": [
            (0x00C0, 0x00FF),  # Latin-1 Supplement（包含 á à ã ạ ...）
            (0x0100, 0x017F),  # Latin Extended-A
            (0x0180, 0x024F),  # Latin Extended-B
            (0x1E00, 0x1EFF),  # Latin Extended Additional
            (0x0300, 0x036F),  # Combining Diacritical Marks
        ],
        "dictionary": [
            'dictionary/vi_dictionary_txt/Viet11K.txt','dictionary/vi_dictionary_txt/Viet22K.txt','dictionary/vi_dictionary_txt/Viet39K.txt','dictionary/vi_dictionary_txt/Viet74K.txt'
        ],
        'latin_letter_ranges':[(0x0041, 0x007A)]
    }
}

now_str=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# print(now_str)
os.makedirs(f'result/result_{now_str}', exist_ok=True)
result_file_dir=f'result/result_{now_str}'

class Test_Th_LangDetect(baselangdetect):
    lang = "th"
    unicode_range = LANG_CONFIG[lang]["unicode_ranges"]
    dictionary = LANG_CONFIG[lang]["dictionary"]
    result_file = f'{result_file_dir}/result_{lang}.csv'
    latin_letter_ranges = LANG_CONFIG[lang]['latin_letter_ranges']

class Test_ar_LangDetect(baselangdetect):
    lang = "ar"
    unicode_range = LANG_CONFIG[lang]["unicode_ranges"]
    dictionary = LANG_CONFIG[lang]["dictionary"]
    result_file = f'{result_file_dir}/result_{lang}.csv'
    latin_letter_ranges = LANG_CONFIG[lang]['latin_letter_ranges']

class Test_ind_LangDetect(baselangdetect):
    lang = "ind"
    unicode_range = LANG_CONFIG[lang]["unicode_ranges"]
    dictionary = LANG_CONFIG[lang]["dictionary"]
    result_file = f'{result_file_dir}/result_{lang}.csv'
    latin_letter_ranges = LANG_CONFIG[lang]['latin_letter_ranges']

class Test_es_LangDetect(baselangdetect):
    lang = "es"
    unicode_range = LANG_CONFIG[lang]["unicode_ranges"]
    dictionary = LANG_CONFIG[lang]["dictionary"]
    result_file = f'{result_file_dir}/result_{lang}.csv'
    latin_letter_ranges = LANG_CONFIG[lang]['latin_letter_ranges']

class Test_ptbr_LangDetect(baselangdetect):
    lang = "pt-br"
    unicode_range = LANG_CONFIG[lang]["unicode_ranges"]
    dictionary = LANG_CONFIG[lang]["dictionary"]
    result_file = f'{result_file_dir}/result_{lang}.csv'
    latin_letter_ranges = LANG_CONFIG[lang]['latin_letter_ranges']

class Test_vn_LangDetect(baselangdetect):
    lang = "vn"
    unicode_range = LANG_CONFIG[lang]["unicode_ranges"]
    dictionary = LANG_CONFIG[lang]["dictionary"]
    result_file = f'{result_file_dir}/result_{lang}.csv'
    latin_letter_ranges = LANG_CONFIG[lang]['latin_letter_ranges']

