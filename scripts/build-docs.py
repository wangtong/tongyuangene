# -*- coding: utf-8 -*-
"""从飞书导出的 Markdown 生成云平台使用说明文档页。"""
from __future__ import annotations

import html
import re
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "基因学苑生物云平台使用说明（2026版）.md"
OUT_DIR = ROOT

SECTION_FILES = [
    ("docs-login.html", "二、如何登录"),
    ("docs-software.html", "三、管理生物软件"),
    ("docs-container.html", "四、使用容器管理生物软件"),
    ("docs-database.html", "五、生物数据库目录"),
    ("docs-positron.html", "六、通过 Positron 使用 R 和 Python"),
    ("docs-rstudio.html", "七、Rstudio 环境使用"),
    ("docs-tmux.html", "八、Tmux 不间断会话"),
    ("docs-ai-tools.html", "九、使用 AI 功能"),
    ("docs-vscode.html", "十、安装和使用 VSCode"),
    ("docs-faq-cloud.html", "十一、常见问题"),
    ("docs-skills.html", "十二、生物信息技能"),
]

SECTION_PATTERN = re.compile(r"^# ([一二三四五六七八九十]+、.+)$", re.M)


def normalize_title(raw: str) -> str:
    t = raw.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def make_id(title: str, used: set[str]) -> str:
    base = re.sub(r"[^\w\u4e00-\u9fff]+", "-", clean_md_text(title).strip()).strip("-").lower()
    if not base:
        base = hashlib.md5(title.encode("utf-8")).hexdigest()[:10]
    candidate = base[:48]
    n = 2
    while candidate in used:
        candidate = f"{base[:44]}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def clean_md_text(text: str) -> str:
    """去掉飞书/ Markdown 导出中的反斜杠转义。"""
    text = re.sub(r"\\([.+#\-_()\[\]+])", r"\1", text)
    text = re.sub(r"\\([a-zA-Z])", r"\1", text)
    return text


def normalize_heading_title(title: str) -> str:
    """标题去掉 ** 等 Markdown 标记，供目录与锚点使用。"""
    title = clean_md_text(title)
    title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)
    title = re.sub(r"\*(.+?)\*", r"\1", title)
    return title.strip()


def inline_format(text: str) -> str:
    text = clean_md_text(text)
    bold_parts: list[str] = []

    def _bold(m: re.Match[str]) -> str:
        bold_parts.append(m.group(1))
        return f"\ue000{len(bold_parts) - 1}\ue001"

    text = re.sub(r"\*\*(.+?)\*\*", _bold, text)
    text = html.escape(text)
    for i, part in enumerate(bold_parts):
        text = text.replace(f"\ue000{i}\ue001", f"<strong>{html.escape(part)}</strong>")
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2).replace(chr(92), ""))}" rel="noopener noreferrer">{m.group(1)}</a>',
        text,
    )
    return text


def parse_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        if not line.strip():
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return ""
    head = rows[0]
    body = rows[2:] if re.match(r"^[-:\s|]+$", "|".join(rows[1])) else rows[1:]
    out = ['<div class="table-wrap"><table class="data-table"><thead><tr>']
    for c in head:
        out.append(f"<th>{inline_format(c)}</th>")
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for c in row:
            out.append(f"<td>{inline_format(c)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def md_to_html(md: str) -> tuple[str, list[tuple[str, str, int]]]:
    """返回 HTML 与 TOC 项 (id, title, level)。"""
    lines = md.splitlines()
    used_ids: set[str] = set()
    toc: list[tuple[str, str, int]] = []
    out: list[str] = []
    i = 0

    def push_heading(level: int, title: str):
        title = normalize_heading_title(title)
        hid = make_id(title, used_ids)
        toc.append((hid, title, level))
        tag = {2: "h2", 3: "h3", 4: "h4", 5: "h5"}.get(level, "h3")
        out.append(f'<{tag} id="{hid}">{inline_format(title)}</{tag}>')

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code = html.escape("\n".join(code_lines))
            cls = "code-block doc-code"
            if lang:
                cls += f" doc-code-{lang.lower().replace(' ', '-')}"
            out.append(f'<pre class="{cls}"><code>{code}</code></pre>')
            i += 1
            continue

        if line.startswith("|") and "|" in line[1:]:
            tbl = []
            while i < len(lines) and lines[i].startswith("|"):
                tbl.append(lines[i])
                i += 1
            out.append(parse_table(tbl))
            continue

        m = re.match(r"^(#{1,5})\s+(.+)$", line)
        if m:
            level = len(m.group(1)) + 1
            if level > 5:
                level = 5
            title = m.group(2).strip()
            if level == 2 and re.match(r"^[一二三四五六七八九十]+、", title):
                pass
            else:
                push_heading(level, title)
            i += 1
            continue

        if re.match(r"^!\[.*?\]\((.+?)\)\s*$", line):
            url = re.match(r"^!\[.*?\]\((.+?)\)\s*$", line).group(1)
            out.append(
                f'<figure class="doc-figure">'
                f'<img src="{html.escape(url)}" alt="说明配图" loading="lazy" '
                f'onerror="this.closest(\'figure\').classList.add(\'is-broken\')">'
                f'<figcaption class="doc-figure-cap">操作示意图（若无法加载，请参考飞书原版文档）</figcaption>'
                f"</figure>"
            )
            i += 1
            continue

        if re.match(r"^[-*]\s+", line) or re.match(r"^\d+\.\s+", line):
            ordered = bool(re.match(r"^\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>")
            while i < len(lines) and (
                re.match(r"^[-*]\s+", lines[i]) or re.match(r"^\d+\.\s+", lines[i])
            ):
                item = re.sub(r"^[-*]\s+|^\d+\.\s+", "", lines[i]).strip()
                if item and item != "-":
                    out.append(f"<li>{inline_format(item)}</li>")
                i += 1
            out.append(f"</{tag}>")
            continue

        if not line.strip():
            i += 1
            continue

        if line.strip() in ("-", "*"):
            i += 1
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(
            ("#", "|", "!", "```")
        ) and not re.match(r"^[-*]\s+", lines[i]) and not re.match(r"^\d+\.\s+", lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            out.append(f"<p>{inline_format(' '.join(para))}</p>")
            continue

        i += 1

    return "\n".join(out), toc


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(text))
    sections: dict[str, str] = {}
    for idx, m in enumerate(matches):
        title = normalize_title(m.group(1))
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections[title] = body
    return sections


def sidebar_index_active(current_file: str) -> str:
    return ' class="is-active"' if current_file == "docs.html" else ""


def sidebar_nav(current_file: str) -> str:
    items = []
    for fname, title in SECTION_FILES:
        active = ' class="is-active"' if fname == current_file else ""
        items.append(f'<li><a href="{fname}"{active}>{html.escape(title)}</a></li>')
    return "\n".join(items)


def docs_index_content() -> str:
    links = []
    for fname, title in SECTION_FILES:
        links.append(
            f'<li class="docs-index-item">'
            f'<a href="{fname}" class="docs-index-link">{html.escape(title)}</a>'
            f"</li>"
        )
    return (
        '<h2 class="doc-page-title">一、文档目录</h2>'
        '<p class="docs-index-intro">基因学苑生物云平台使用说明（2026 版）。点击下方章节进入对应页面：</p>'
        f'<ol class="docs-index-list">{"".join(links)}</ol>'
    )


def page_toc(toc: list[tuple[str, str, int]]) -> str:
    if not toc:
        return '<li><span class="doc-toc-empty">本页无子目录</span></li>'
    parts: list[str] = []
    sub_open = False
    for hid, title, level in toc:
        if level >= 4:
            if not sub_open:
                parts.append('<li><ul class="doc-toc-sub">')
                sub_open = True
            parts.append(f'<li><a href="#{hid}">{html.escape(title)}</a></li>')
        else:
            if sub_open:
                parts.append("</ul></li>")
                sub_open = False
            parts.append(f'<li><a href="#{hid}">{html.escape(title)}</a></li>')
    if sub_open:
        parts.append("</ul></li>")
    return "\n".join(parts)


HEADER = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<script>(function(){{var t=localStorage.getItem('ty-theme')||'light';document.documentElement.setAttribute('data-theme',t);}})();</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | 技术文档</title>
<meta name="description" content="基因学苑生物云平台使用说明（2026版）">
<link rel="stylesheet" href="css/style.css">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23cc0000'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-family='Arial' font-size='18' font-weight='bold' fill='white'%3E同%3C/text%3E%3C/svg%3E">
</head>
<body data-page="docs">
<header class="header">
    <nav class="navbar">
        <a href="index.html" class="logo">
            <span class="logo-icon" aria-hidden="true"><svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg" focusable="false" aria-hidden="true"><g transform="rotate(135 22 22)" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"><path d="M8 16 C 16 10 28 10 36 16"/><path d="M8 28 C 16 34 28 34 36 28" opacity="0.7"/><path d="M14 18 L18 26"/><path d="M22 16 L22 28" opacity="0.8"/><path d="M30 18 L26 26"/></g></svg></span>
            <span class="logo-text">
                <span class="logo-name">青岛同源基因</span>
                <span class="logo-en">TONGYUAN GENE</span>
            </span>
        </a>
        <ul class="nav-menu">
            <li><a href="index.html">首页</a></li>
            <li><a href="cloud.html">生物云计算</a></li>
            <li><a href="video.html">生物信息视频课程</a></li>
            <li><a href="ai.html">AI+生物信息</a></li>
            <li><a href="docs.html" class="active">技术文档</a></li>
            <li><a href="about.html">关于我们</a></li>
        </ul>
        <div class="nav-actions">
            <div class="nav-toolbar">
                <button type="button" class="toolbar-btn" id="theme-toggle" aria-label="切换到暗色模式" title="暗色模式">
                    <span class="theme-icon-light" aria-hidden="true">☀️</span>
                    <span class="theme-icon-dark" aria-hidden="true">🌙</span>
                </button>
            </div>
            <a href="about.html" class="btn btn-primary">联系我们</a>
        </div>
        <button class="nav-toggle" aria-label="切换导航">☰</button>
    </nav>
</header>
<section class="subhero subhero-compact">
    <div class="container">
        <div class="breadcrumb">
            <a href="index.html">首页</a> / <a href="docs.html">技术文档</a> / <span>{breadcrumb}</span>
        </div>
        <h1>基因学苑生物云平台使用说明</h1>
        <p>2026 版 · 从登录、传文件到软件环境与 AI 工具</p>
    </div>
</section>
<section class="section section-docs">
    <div class="container">
        <div class="docs-layout docs-layout-3">
            <aside class="docs-sidebar" aria-label="文档章节">
                <h4 class="docs-sidebar-heading"><a href="docs.html"{sidebar_index_active}>一、文档目录</a></h4>
                <nav>
                    <ul class="docs-sidebar-list">
{sidebar}
                    </ul>
                </nav>
            </aside>
            <div class="docs-content">
                <div class="content-block doc-page">
                    {page_title_block}
{content}
                </div>
            </div>
            <aside class="doc-toc" aria-label="本页目录">
                <h4>本页目录</h4>
                <nav>
                    <ul class="doc-toc-main">
{toc}
                    </ul>
                </nav>
            </aside>
        </div>
    </div>
</section>
<footer class="footer">
    <div class="container">
        <div class="footer-top">
            <div class="footer-brand">
                <div class="footer-logo">
                    <span class="logo-icon" aria-hidden="true"><svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg" focusable="false" aria-hidden="true"><g transform="rotate(135 22 22)" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"><path d="M8 16 C 16 10 28 10 36 16"/><path d="M8 28 C 16 34 28 34 36 28" opacity="0.7"/><path d="M14 18 L18 26"/><path d="M22 16 L22 28" opacity="0.8"/><path d="M30 18 L26 26"/></g></svg></span>
                    <span>青岛同源基因</span>
                </div>
                <p>因为专注，所以专业。<br>专注新一代测序技术服务，<br>让生物数据分析触手可及。</p>
            </div>
            <div class="footer-col">
                <h4>产品</h4>
                <ul>
                    <li><a href="cloud.html">生物云计算</a></li>
                    <li><a href="video.html">视频课程</a></li>
                    <li><a href="ai.html">AI+生物信息</a></li>
                    <li><a href="docs.html">技术文档</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>资源</h4>
                <ul>
                    <li><a href="docs-login.html">云平台使用说明</a></li>
                    <li><a href="cloud.html">服务器价格</a></li>
                    <li><a href="video.html">试看视频</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>公司</h4>
                <ul>
                    <li><a href="about.html">关于我们</a></li>
                    <li><a href="about.html#contact">联系方式</a></li>
                </ul>
            </div>
            <div class="footer-col footer-contact">
                <h4>联系我们</h4>
                <p><strong>邮箱</strong>genomics@outlook.com</p>
                <p><strong>地址</strong>山东省青岛市高新区秀园路1号科创慧谷(青岛)科技园 D-2-264</p>
                <p><strong>网址</strong>www.tongyuangene.com</p>
            </div>
        </div>
        <div class="footer-bottom">
            <span>版权所有 © 2026 同源基因</span>
            <span class="footer-legal">
                <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">鲁ICP备19022587号-2</a>
            </span>
        </div>
    </div>
</footer>
<script src="js/main.js"></script>
<script src="js/docs-nav.js"></script>
</body>
</html>
"""


def main():
    text = MD_PATH.read_text(encoding="utf-8")
    sections = split_sections(text)

    for fname, full_title in SECTION_FILES:
        key = full_title
        alt_keys = [
            full_title,
            full_title.replace("Positron", "positron"),
            full_title.replace("VSCode", "vscode"),
            full_title.replace("五、生物", "五、 生物"),
        ]
        body = None
        for k in sections:
            if any(normalize_title(k) == normalize_title(a) for a in alt_keys) or k.startswith(full_title[:2]):
                if full_title[:2] in k:
                    body = sections[k]
                    key = k
                    break
        if body is None:
            for k, v in sections.items():
                if k.startswith(full_title.split("、")[0] + "、"):
                    body = v
                    key = k
                    break
        if body is None:
            raise SystemExit(f"Missing section: {full_title}")

        content_html, toc_items = md_to_html(body)
        breadcrumb = re.sub(r"^[一二三四五六七八九十]+、", "", full_title)
        page = HEADER.format(
            title=html.escape(breadcrumb),
            breadcrumb=html.escape(breadcrumb),
            page_title_block=f'<h2 class="doc-page-title">{html.escape(key)}</h2>',
            sidebar_index_active=sidebar_index_active(fname),
            sidebar=sidebar_nav(fname),
            content=content_html,
            toc=page_toc(toc_items),
        )
        (OUT_DIR / fname).write_text(page, encoding="utf-8", newline="\n")
        print("Wrote", fname)

    index_page = HEADER.format(
        title="文档目录",
        breadcrumb="文档目录",
        page_title_block="",
        sidebar_index_active=sidebar_index_active("docs.html"),
        sidebar=sidebar_nav("docs.html"),
        content=docs_index_content(),
        toc='<li><span class="doc-toc-empty">请从左侧或下方列表选择章节</span></li>',
    )
    (OUT_DIR / "docs.html").write_text(index_page, encoding="utf-8", newline="\n")
    print("Wrote docs.html (index)")


if __name__ == "__main__":
    main()
