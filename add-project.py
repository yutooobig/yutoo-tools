import os, json, shutil, subprocess, sys

"""
用法：
    python3 add-project.py <git仓库地址> [子目录名] [标题]

做的事：
    1. 把仓库克隆到 projects/<子目录名>/
    2. 删掉 .git，避免变成嵌套仓库
    3. 自动往 projects.json 追加一条记录
"""

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    repo = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(repo.rstrip('/')).replace('.git', '')
    title = sys.argv[3] if len(sys.argv) > 3 else name

    root = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(root, 'projects', name)

    if os.path.exists(target):
        print(f'目录已存在：{target}，先删掉再重试')
        sys.exit(1)

    print(f'克隆 {repo} -> projects/{name}')
    subprocess.run(['git', 'clone', '--depth', '1', repo, target], check=True)

    git_dir = os.path.join(target, '.git')
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)

    entry = {'name': name, 'title': title, 'desc': '', 'tags': []}
    data_path = os.path.join(root, 'projects.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if any(p.get('name') == name for p in data):
        print('projects.json 已有同名条目，跳过')
    else:
        data.append(entry)
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'已写入 projects/{name}/，并在 projects.json 注册')

    print('\n检查绝对路径引用（有输出就要改成相对路径）：')
    hits = subprocess.run(
        ['grep', '-rnE', r'(src|href)="/[^/]', target],
        capture_output=True, text=True
    ).stdout.strip()
    print(hits if hits else '  未发现，路径没问题')

    print('\n重新生成首页…')
    subprocess.run([sys.executable, os.path.join(root, 'build.py')])

if __name__ == '__main__':
    main()
