"""给 HTML 读书笔记生成可点击的目录（重复运行会先删掉旧目录再重建）。

用法：python3 tools/add_toc.py notes/xxx.html [...]
会给每个 h2/h3 加上 id，并在第一个 <h2> 之前插入 <nav class="toc">。
"""
import re
import sys

CSS = """
nav.toc{background:var(--card);border-radius:8px;padding:14px 18px;margin:24px 0}
nav.toc>b{display:block;margin-bottom:6px}
nav.toc ol{margin:0;padding-left:1.1em}nav.toc ol ol{padding-left:1.2em;font-size:14px}
nav.toc li{margin:2px 0}nav.toc a{color:var(--fg);text-decoration:none}nav.toc a:hover{color:var(--red)}
h2,h3{scroll-margin-top:16px}
a.top{position:fixed;right:16px;bottom:16px;background:var(--card);color:var(--muted);border-radius:20px;padding:6px 12px;font-size:13px;text-decoration:none;box-shadow:0 1px 4px rgba(0,0,0,.15)}
"""


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def process(path):
    html = open(path, encoding="utf-8").read()
    html = re.sub(r'\s*<nav class="toc"[^>]*>.*?</nav>', "", html, flags=re.S)
    html = re.sub(r'\s*<a class="top"[^>]*>.*?</a>', "", html)
    html = re.sub(r"\n/\* toc \*/.*?/\* /toc \*/", "", html, flags=re.S)

    items, n2, n3 = [], 0, 0

    def tag(m):
        nonlocal n2, n3
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        attrs = re.sub(r'\s*id="[^"]*"', "", attrs)
        if level == "2":
            n2, n3 = n2 + 1, 0
            hid = f"s{n2}"
        else:
            n3 += 1
            hid = f"s{n2}-{n3}"
        items.append((level, hid, strip_tags(inner)))
        return f'<h{level} id="{hid}"{attrs}>{inner}</h{level}>'

    html = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", tag, html, flags=re.S)

    out, open_sub = ['<nav class="toc" id="toc"><b>目录</b><ol>'], False
    for level, hid, text in items:
        if level == "2":
            if open_sub:
                out.append("</ol></li>")
                open_sub = False
            elif len(out) > 1:
                out.append("</li>")
            out.append(f'<li><a href="#{hid}">{text}</a>')
        else:
            if not open_sub:
                out.append("<ol>")
                open_sub = True
            out.append(f'<li><a href="#{hid}">{text}</a></li>')
    out.append("</ol></li>" if open_sub else "</li>")
    out.append("</ol></nav>")
    nav = "\n".join(out)

    html = html.replace("<h2 ", nav + "\n\n<h2 ", 1)
    html = html.replace("</main>", '<a class="top" href="#toc">↑ 目录</a>\n</main>', 1)
    html = html.replace("</style>", "/* toc */" + CSS + "/* /toc */\n</style>", 1)
    open(path, "w", encoding="utf-8").write(html)
    print(path, len(items), "headings")


for p in sys.argv[1:]:
    process(p)
