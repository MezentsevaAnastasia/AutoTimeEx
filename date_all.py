import re
import pandas as pd
from ahocorapy.keywordtree import KeywordTree


class Pattern:

    def __init__(self):
        pass

    def _extract_date_with_numbers(self, tokens):
        threeGroupsDate = r'\d{2,4}[\/\-.]\d{2}[.\-\/]\d{2,4}'  # 14.12.1999, 1999.12.14, 12.14.1999
        yearFirst = r'[1-9]\d{3}[\.-\/][0-1]\d[\.-\/][0-3]\d'  # 1999.14.12
        yearLast = r'[0-3]\d{1}[\.-\/][0,1]\d[\.-\/][1-9]\d{3}'  # 14.12.1999
        yearLastShort = r'[0-3]\d{1}[\.-\/][0,1]\d[\.-\/][1-9]\d'  # 14.12.99
        monthAndYear = r'[0,1]\d[\.-\/][1-2]\d{3}'  # 12.1999
        dateAndMonth = r'[0-3]\d[\.\/-][0,1]\d'  # 14.12, 03.01
        finalRuleList = [threeGroupsDate, yearFirst, yearLast, yearLastShort, monthAndYear, dateAndMonth]
        finalRule = '|'.join(finalRuleList)
        text = ' '.join(tokens)
        result = re.findall(finalRule, text)
        return result[0]


    def extract_date_type1(self, tokens):
        """
        типы соответствуют таблице classification of TE
        :param tokens:
        :return:
        """
        text = ' '.join(tokens)
        pattern_type = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon.|Tue.Wen.|Thu|Fri|Sat|Sun),.(January|February|March|April|May|June|July|August|September|October|November|December).\d,\d{4}'
        result = re.findall(pattern_type, text)
        return result[0]


    def extract_date_type2(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon.|Tue.Wen.|Thu.|Fri.|Sat.|Sun.),.\d{1,2}.(January|February|March|April|May|June|July|August|September|October|November|December).\d{4}'
        result = re.findall(pattern_type, text)
        return result[0]


    def extract_date_type3(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon.|Tue.Wen.|Thu.|Fri.|Sat.|Sun.).(the).\d{1,2}(th|d).(of).(January|February|March|April|May|June|July|August|September|October|November|December),.\d{4}'
        result = re.findall(pattern_type, text)
        return result[0]


    def extract_date_type4(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'\d{1,2}(th|d).(of).(January|February|March|April|May|June|July|August|September|October|November|December).\d{4}'
        result = re.findall(pattern_type, text)
        return result[0]


    def extract_date_type5(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'the.\d{1,2}(th|d).(of).(January|February|March|April|May|June|July|August|September|October|November|December),.\d{4}'
        result = re.findall(pattern_type, text)
        return result[0], 'DATE'


    def extract_date_type6(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan.|Feb.|Mar.|Apr.|Aug.|Sept.|Oct.|Nov.|Dec.).\d'
        result = re.findall(pattern_type, text)
        return result[0]


    def extract_date_type7(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'\d{1,2}.(January|February|March|April|May|June|July|August|September|October|November|December|Jan.|Feb.|Mar.|Apr.|Aug.|Sept.|Oct.|Nov.|Dec.)'
        result = re.findall(pattern_type, text)
        return result[0]



    def extract_date_type8(self, tokens):
        text = ' '.join(tokens)
        pattern_type = r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan.|Feb.|Mar.|Apr.|Aug.|Sept.|Oct.|Nov.|Dec.).\d{4}'
        result = re.findall(pattern_type, text)
        return result[0]


    def merge_date_extractions(self, tokens):
        """
        соединяем все рещультаты в одно целое
        :param tokens: входной список токенов
        :return: список из токенов, которые выделились всеми регулярными выражениями
        """
        extracts = [extract_date_type1(tokens), extract_date_type2(tokens), extract_date_type3(tokens),
                    extract_date_type4(tokens), extract_date_type5(tokens), extract_date_type6(tokens),
                    extract_date_type7(tokens), extract_date_type8(tokens)]
        # очищаем от нулевых элементов
        extracts = list(filter(None, extracts))
        return extracts

    def _create_kw_tree(self, tokens_date):
        """
        Создаёт суффиксное дерево для конкретного типа временного выражения
        :param time_expressions:
        :return: суффиксное дерево
        """
        kwtree = KeywordTree()
        for date in tokens_date:
            tokens = date.split()
            kwtree.add(tokens)
        kwtree.finalize()
        return kwtree

    def _search_phrases(self, all_tokens, ids_time_expressions, kw_tree: KeywordTree, type):
        """
        Ищет временные выражения в тексте, сохраняет в словарь ids_time_expressions для позиции токена в тексте тип
        временного выражения этого токена
        :param all_tokens: токенизированный текст
        :param ids_time_expressions: словарь, где ключ - позиция токена в тексте, значение - тип этого токена в BIO
        разметке; заполняется в этом методе
        :param kw_tree: суффиксное дерево соответствующего типа временного выражения
        :param type: тип временного выражения
        :return:
        """
        for ids in kw_tree.search_all(all_tokens):
            tokens = ids[0]
            for i, token in enumerate(tokens):
                if i == 0:
                    ids_time_expressions[ids[1] + i] = 'B-{}'.format(type)
                else:
                    ids_time_expressions[ids[1] + i] = 'I-{}'.format(type)

    def _get_token_id2token_type(self, all_tokens, type):
        """
        Создаём словарь, в котором ключ - позиция токена в тексте, значение - его тип в BIO-разметке
        :param all_tokens: токенизированный текст
        :param time_expressions: словарь, который для каждого типа временного выражения содержит список токенов из
        текста
        :return: словарь, в котором ключ - позиция токена в тексте, значение - его тип в BIO-разметке
        """
        tokens_date = self.merge_date_extractions(all_tokens)
        time_tree = self._create_kw_tree(tokens_date)
        token_id2token_type = dict()
        self._search_phrases(all_tokens, token_id2token_type, time_tree, type)
        return token_id2token_type

    def extract(self, text):
        all_tokens = text.split()
        token_id2token_type = self._get_token_id2token_type(all_tokens, 'DATE')

        for i, token in enumerate(all_tokens):
            if i in token_id2token_type:
                print(token, token_id2token_type[i])

            else:
                print(token, 'O')


if __name__ == '__main__':
    pattern = Pattern()
    pattern.extract('It was Friday , October 1 , 1999')

# считываем файлы с тетовой выборкой
data = pd.read_csv("", error_bad_lines=False, encoding="utf-8")
test_text = data[]
# make file for all test dataset
if __name__ == '__main__':
    pattern = Pattern()
    pattern.extract(test_text)

