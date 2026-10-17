#!/usr/bin/env python3
"""
把 projects.json 渲染成静态的 index.html。

用法：
    python3 build.py

加完项目、改完 projects.json 后跑一次，然后把生成的 index.html 一起提交。
生成结果是纯 HTML，不依赖任何 JavaScript 就能正常显示和跳转。
"""

import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(ROOT, 'projects')


def load_projects():
    path = os.path.join(ROOT, 'projects.json')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('projects', [])


def esc(value):
    return html.escape(str(value or ''), quote=True)


def render_card(p):
    name = p['name'].strip('/')
    url = p.get('url') or './projects/%s/' % name
    title = p.get('title') or name
    desc = p.get('desc') or ''
    tags = p.get('tags') or []

    tag_html = ''
    if tags:
        tag_html = '\n        <div class="tags">%s</div>' % ''.join(
            '<span class="tag">%s</span>' % esc(t) for t in tags
        )

    key = ' '.join([title, desc, name] + list(tags))
    return (
        '<a class="card" href="%s" data-key="%s">\n'
        '        <h2>%s</h2>\n'
        '        <p>%s</p>%s\n'
        '      </a>'
    ) % (esc(url), esc(key), esc(title), esc(desc), tag_html)


def main():
    projects = load_projects()

    missing = []
    for p in projects:
        d = os.path.join(PROJECTS_DIR, p['name'].strip('/'))
        if not os.path.isdir(d):
            missing.append(p['name'])
        elif not os.path.exists(os.path.join(d, 'index.html')):
            print('提示：projects/%s/ 下没有 index.html' % p['name'].strip('/'))

    template_path = os.path.join(ROOT, '_template.html')
    with open(template_path, encoding='utf-8') as f:
        tpl = f.read()

    cards = '\n      '.join(render_card(p) for p in projects) or '<p>还没有项目，往 projects/ 里放一个吧。</p>'

    out = (tpl
           .replace('{{CARDS}}', cards)
           .replace('{{COUNT}}', str(len(projects)))
           .replace('{{YEAR}}', str(__import__('datetime').date.today().year)))

    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

    print('已生成 index.html，共 %d 个项目' % len(projects))
    if missing:
        print('警告：这些项目目录不存在 -> %s' % ', '.join(missing))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
