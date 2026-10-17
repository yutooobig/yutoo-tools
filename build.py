#!/usr/bin/env python3
"""
把 projects/ 目录和 projects.json 合并，渲染成静态的 index.html。

用法：
    python3 build.py

规则：
  - projects/ 下每个带 index.html 的子目录，都会被自动收进首页（标题默认用目录名）
  - projects.json 用来补充标题、描述、标签，也可以放外链项目（带 url 字段）
  - json 里登记了但目录不存在的本地项目会被跳过，避免死链

改完任何项目文件后重新跑一次，再把生成的 index.html 一起提交。
生成结果是纯 HTML，不依赖 JavaScript 就能正常显示和跳转。
"""

import datetime
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(ROOT, 'projects')


def load_json():
    path = os.path.join(ROOT, 'projects.json')
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print('projects.json 格式错误：%s（第 %d 行第 %d 列）' % (e.msg, e.lineno, e.colno))
        sys.exit(1)
    if isinstance(data, dict):
        data = data.get('projects', [])
    return data if isinstance(data, list) else []


def scan_dirs():
    """返回 projects/ 下有 index.html 的目录名列表"""
    if not os.path.isdir(PROJECTS_DIR):
        return []
    names = []
    for entry in sorted(os.listdir(PROJECTS_DIR)):
        if entry.startswith('.'):
            continue
        d = os.path.join(PROJECTS_DIR, entry)
        if not os.path.isdir(d):
            continue
        if os.path.exists(os.path.join(d, 'index.html')):
            names.append(entry)
        else:
            print('跳过 projects/%s/：里面没有 index.html' % entry)
    return names


def is_local(p):
    url = p.get('url')
    return not url or str(url).startswith('./projects/')


def merge():
    declared = load_json()
    found = scan_dirs()

    by_name = {}
    for p in declared:
        if not p.get('name'):
            continue
        by_name[p['name'].strip('/')] = p

    merged, auto, dropped = [], [], []

    for p in declared:
        name = str(p.get('name', '')).strip('/')
        if not name:
            continue
        if is_local(p):
            if not os.path.isdir(os.path.join(PROJECTS_DIR, name)):
                dropped.append(name)
                continue
        merged.append(p)

    for name in found:
        if name not in by_name:
            merged.append({'name': name, 'title': name, 'desc': '', 'tags': []})
            auto.append(name)

    return merged, auto, dropped


def esc(value):
    return html.escape(str(value or ''), quote=True)


def render_card(p):
    name = str(p['name']).strip('/')
    url = p.get('url') or './projects/%s/' % name
    title = p.get('title') or name
    desc = p.get('desc') or ''
    tags = p.get('tags') or []

    tag_html = ''
    if tags:
        tag_html = '\n        <div class="tags">%s</div>' % ''.join(
            '<span class="tag">%s</span>' % esc(t) for t in tags
        )

    key = ' '.join([title, desc, name] + [str(t) for t in tags])
    return (
        '<a class="card" href="%s" data-key="%s">\n'
        '        <h2>%s</h2>\n'
        '        <p>%s</p>%s\n'
        '      </a>'
    ) % (esc(url), esc(key), esc(title), esc(desc), tag_html)


def main():
    projects, auto, dropped = merge()

    template_path = os.path.join(ROOT, '_template.html')
    with open(template_path, encoding='utf-8') as f:
        tpl = f.read()

    cards = '\n      '.join(render_card(p) for p in projects) or \
        '<p>还没有项目，往 projects/ 里放一个吧。</p>'

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    out = (tpl
           .replace('{{CARDS}}', cards)
           .replace('{{COUNT}}', str(len(projects)))
           .replace('{{YEAR}}', str(datetime.date.today().year))
           .replace('{{BUILT_AT}}', now))

    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

    print('已生成 index.html · %d 个项目 · %s' % (len(projects), now))
    for p in projects:
        print('  - %-14s %s' % (str(p['name']).strip('/'), p.get('title') or p['name']))
    if auto:
        print('自动收录（未在 projects.json 登记，标题用目录名）-> %s' % ', '.join(auto))
    if dropped:
        print('已跳过（projects.json 有登记但目录不存在）-> %s' % ', '.join(dropped))
    if not projects:
        print('提示：把项目文件放进 projects/<名字>/，确保有 index.html')
    return 0


if __name__ == '__main__':
    sys.exit(main())
