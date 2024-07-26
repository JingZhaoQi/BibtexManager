import requests
import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from scholarly import scholarly
import os
import json
from fake_useragent import UserAgent
import requests

def check_network():
    try:
        response = requests.get("https://www.baidu.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 设置自定义的 fake_useragent 数据
custom_path = get_resource_path('fake_useragent.json')
with open(custom_path, 'r') as f:
    custom_data = json.load(f)

ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
ua.data = custom_data
ua.data_randomize = custom_data['randomize']


def search_inspire(query):
    base_url = "https://inspirehep.net/api/literature"
    params = {
        "q": query,
        "format": "bibtex"
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # 这将引发一个异常，如果状态码不是200
        if response.text.strip():
            return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error searching INSPIRE: {e}")
    return None

def search_google_scholar(query):
    try:
        search_query = scholarly.search_pubs(query)
        publication = next(search_query)
        return publication
    except:
        return None

def is_bib_code(query):
    # BibTeX 标识符通常是这样的格式：Author:YYYYxxx
    # 其中 YYYY 是年份，xxx 是一些字母
    pattern = r'^[A-Za-z]+:\d{4}[a-z]{2,3}$'
    return bool(re.match(pattern, query))

def get_bibtex(query, is_title=True):
    if not query.strip():
        return None

    original_query = query

    if is_title and not is_bib_code(query):
        query = query.replace(":", "")
    
    bibtex = search_inspire(query)
    if bibtex:
        return bibtex

    if query != original_query:
        bibtex = search_inspire(original_query)
        if bibtex:
            return bibtex

    gs_result = search_google_scholar(original_query)
    if gs_result:
        arxiv_id = extract_arxiv_id(gs_result)
        if arxiv_id:
            inspire_query = f"arXiv:{arxiv_id}"
            bibtex = search_inspire(inspire_query)
            if bibtex:
                return bibtex

        # 如果没有找到 arXiv ID 或 INSPIRE 搜索失败，尝试使用标题再次搜索 INSPIRE
        title = gs_result.get('bib', {}).get('title', '')
        if title:
            bibtex = search_inspire(title)
            if bibtex:
                return bibtex

        # 如果还是失败，则返回处理过的 Google Scholar BibTeX
        return process_google_scholar_bibtex(gs_result)

    return None

def extract_arxiv_id(gs_result):
    """
    从 Google Scholar 结果中提取 arXiv ID。
    
    :param gs_result: Google Scholar 搜索结果
    :return: arXiv ID 或 None
    """
    if not gs_result:
        return None

    # 定义可能包含 arXiv ID 的字段
    possible_fields = ['eprint', 'journal', 'url','venue']

    # 首先检查 bib 字典
    if isinstance(gs_result, dict) and 'bib' in gs_result:
        bib = gs_result['bib']
        for field in possible_fields:
            if field in bib:
                arxiv_id = extract_arxiv_id_from_string(bib[field])
                if arxiv_id:
                    return arxiv_id

    # 如果在 bib 中没有找到，检查整个 gs_result
    if isinstance(gs_result, dict):
        for field in possible_fields:
            if field in gs_result:
                arxiv_id = extract_arxiv_id_from_string(gs_result[field])
                if arxiv_id:
                    return arxiv_id

    # 如果以上都失败，将整个结果转为字符串并搜索
    return extract_arxiv_id_from_string(str(gs_result))

def extract_arxiv_id_from_string(text):
    """
    从给定的字符串中提取 arXiv ID。
    
    :param text: 可能包含 arXiv ID 的字符串
    :return: arXiv ID 或 None
    """
    if not isinstance(text, str):
        return None

    # 匹配 arXiv:YYMM.NNNNN 或 arXiv:YYMM.NNNNNvN 格式
    match = re.search(r'arXiv:(\d{4}\.\d{4,5}(v\d+)?)', text, re.IGNORECASE)
    if match:
        return match.group(1)

    # 匹配 arxiv.org/abs/YYMM.NNNNN 格式
    match = re.search(r'arxiv.org/abs/(\d{4}\.\d{4,5}(v\d+)?)', text, re.IGNORECASE)
    if match:
        return match.group(1)

    return None

def process_google_scholar_bibtex(gs_result):
    bibtex = scholarly.bibtex(gs_result)
    
    # 移除 abstract 字段
    bibtex = re.sub(r'\s*abstract = {[^}]*},\n', '', bibtex)
    
    return bibtex

def get_bibtex_from_citations(latex_text):
    citation_pattern = r'\\cite[pt]?{([^}]+)}'
    citations = re.findall(citation_pattern, latex_text)
    all_bibtex = ""
    processed_keys = set()
    not_found_entries = []
    
    for citation in citations:
        keys = citation.split(',')
        for key in keys:
            key = key.strip()
            if key not in processed_keys:
                bibtex = get_bibtex(key, is_title=False)
                if bibtex:
                    all_bibtex += f"{bibtex}\n\n"
                    processed_keys.add(key)
                else:
                    not_found_entries.append(key)
    
    return all_bibtex.strip(), not_found_entries

def get_entries_from_content(content):
    parser = BibTexParser()
    parser.expect_multiple_parse = True
    parser.ignore_nonstandard_types = False
    bib_database = bibtexparser.loads(content, parser)
    return bib_database.entries

def update_bibtex_file(new_content, existing_content):
    existing_entries = get_entries_from_content(existing_content) if existing_content.strip() else []
    new_entries = get_entries_from_content(new_content)
    
    existing_ids = {entry['ID'].lower(): entry for entry in existing_entries}
    added_entries = []
    skipped_entries = []
    
    for entry in new_entries:
        lower_id = entry['ID'].lower()
        if lower_id not in existing_ids:
            existing_ids[lower_id] = entry
            added_entries.append(entry['ID'])
        else:
            skipped_entries.append(entry['ID'])
    
    writer = BibTexWriter()
    writer.indent = '    '
    writer.display_order = ('title', 'author', 'year', 'journal', 'volume', 'number', 'pages', 'doi', 'arxiv')
    
    writer.add_trailing_commas = True
    writer.comma_first = False
    writer.string_bracket_type = '{'  # 使用单个大括号
    
    # 创建一个新的 BibDatabase 对象
    updated_db = bibtexparser.bibdatabase.BibDatabase()
    updated_db.entries = list(existing_ids.values())
    
    # 遍历所有条目，移除标题中的额外括号
    for entry in updated_db.entries:
        if 'title' in entry:
            entry['title'] = entry['title'].strip('{}')

    updated_bib = writer.write(updated_db)
    return updated_bib, added_entries, skipped_entries

def get_existing_entries(file_path):
    if not file_path or not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as file:
        existing_content = file.read()
    
    return get_entries_from_content(existing_content)

def clean_bib_content(bib_content):
    parser = BibTexParser()
    bib_database = bibtexparser.loads(bib_content, parser)
    
    entries_dict = {}
    removed_entries = []
    for entry in bib_database.entries:
        lower_id = entry['ID'].lower()
        if lower_id in entries_dict:
            removed_entries.append(entry['ID'])
        else:
            entries_dict[lower_id] = entry
    
    bib_database.entries = list(entries_dict.values())
    writer = BibTexWriter()
    writer.indent = '    '
    writer.display_order = ('title', 'author', 'year', 'journal', 'volume', 'number', 'pages', 'doi', 'arxiv')
    return writer.write(bib_database), removed_entries

def check_and_clean_bib(bib_file_path):
    with open(bib_file_path, 'r') as bibtex_file:
        bib_content = bibtex_file.read()
    
    cleaned_bib, removed_entries = clean_bib_content(bib_content)
    
    with open(bib_file_path, 'w') as bibtex_file:
        bibtex_file.write(cleaned_bib)
    
    return removed_entries
