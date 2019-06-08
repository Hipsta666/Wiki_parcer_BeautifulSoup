import re, os
from bs4 import BeautifulSoup
import time
start_time = time.time()

def links(start, path):
    """Функция возвращает все ссылки из папки с путем path, родителем которых является start."""
    with open("./wiki/" + start) as file:
        link_re = set(re.findall(r'(?<=/wiki/)[\w()]+', file.read()))
        set_links = link_re & set(os.listdir(path)) - {start}
        return set_links


def bfs(graph, start, end, path):
    """Функция выполняет обход графа graph в ширину от вершины start до вершины end.
        Граф представляется в виде списка смежности (словарь множеств, в частности)."""
    fired = set(start)
    connection = dict()
    order = [start]
    while order:
        way = order.pop(0)
        for neighbour in graph[way]:
            if neighbour not in fired:
                fired.add(neighbour)
                order.append(neighbour)
                connection[neighbour] = way
            if end in links(neighbour, path):
                connection[end] = neighbour
                return connection
            graph[neighbour] = links(neighbour, path)


def surprise(start, end, lst, path):
    """Функция возвращает кратчайший путь от start до end в виде списка"""
    parents = bfs({start: links(start, path)}, start, end, path)
    while end != start:
        lst.append(end)
        end = parents[end]
        if end == start:
            lst.append(start)
    return lst[::-1]


def parse(start, end, path):
    """Функция соберает статистику по нескольким страницам из wikipedia и возвращает её в виде словаря.
        Объектами сататистических данных являются содержание на странице картинок определённой ширины,
        количество заголовков, первая буква текста внутри которых соответствует заглавной букве E, T или C,
        длина максимальной последовательности ссылок, между которыми нет других тегов, открывающихся или закрывающихся,
        количество списков (ul, ol), не вложенных в другие списки."""
    out = {}
    for file in surprise(start, end, [], path):
        out[file] = [0, 0, 0, 0]
        with open(path + file) as data:
            soup = BeautifulSoup(data, "lxml")
        body = soup.find(id="bodyContent")
        for item in body.find_all('img', width=True):
            width = item['width']
            if int(width) >= 200:
                out[file][0] += 1

        for i in body.select('h1, h2, h3, h4, h5, h6'):
            if i.text[0] in 'ETC':
                out[file][1] += 1

        len_links = 0
        for _ in body.find_all('a'):
            brothers = body.a.find_next_siblings()
            other_len = 1
            for link in brothers:
                if link.name == 'a':
                    other_len += 1
                elif link.name != 'a':
                    break
            if len_links < other_len:
                len_links = other_len
            body.a = body.a.find_next("a")
        out[file][2] = len_links

        for item in body.select('ol, ul'):
            not_in = [i.name for i in item.parents]
            if 'ul' and 'li' not in not_in:
                out[file][3] += 1
    return out

print(parse( 'Stone_Age', 'Python_(programming_language)', './wiki/'))

print(time.time() - start_time)
