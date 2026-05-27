# 青岛同源基因科技有限责任公司 - 企业官网

一个参照红帽官网 (redhat.com/zh-cn) 设计风格构建的企业官网，为 **青岛同源基因科技有限责任公司** (www.tongyuangene.com) 量身打造。

## 项目简介

本项目是一个使用纯 HTML / CSS / JavaScript 构建的静态官网，无需后端、无需构建工具，双击即可在浏览器中查看。

整体设计采用红帽官网风格：
- 红色 + 深色基调
- 干净简洁的卡片式布局
- 大量留白与清晰的视觉层级
- 现代化的 Hero、CTA、统计与文章网格区块

## 目录结构

```
tongyuan/
├── index.html          # 首页
├── cloud.html          # 生物云计算
├── video.html          # 生物信息视频课程
├── ai.html             # AI+生物信息
├── training.html       # 线下培训
├── docs.html           # 技术文档
├── about.html          # 关于我们
├── css/
│   └── style.css       # 共享样式表
├── js/
│   ├── main.js         # 共享脚本（导航、主题）
│   └── docs-nav.js     # 技术文档左侧目录高亮
├── images/             # 9 张本地 SVG 矢量插图
└── README.md
```

## 页面说明

| 页面 | 文件 | 主要内容 |
|---|---|---|
| 首页 | `index.html` | Hero、公司介绍、4 大核心产品（云计算、视频、AI、技术文档）、3 大特色板块、数据统计、技术主题文章、CTA |
| 生物云计算 | `cloud.html` | 平台介绍、计算资源、使用规范、价格表、服务器配置、购买流程 |
| 视频课程 | `video.html` | 课程数据、服务内容、10 大特色、课程目录、上机环境、购买方式 |
| AI+生物信息 | `ai.html` | 《驯龙高手》课程介绍、10 大课程特色、试看视频、解锁流程、课程对比 |
| 技术文档 | `docs.html` | 快速开始、常用工具命令、分析流程模板、最佳实践、FAQ |
| 关于我们 | `about.html` | 公司简介、核心理念、发展历程、联系方式、微信添加 |

## 如何运行

无需任何依赖，直接：

1. 在浏览器中双击打开 `index.html`，或
2. 在项目根目录启动一个简单的本地服务器，例如：

   ```bash
   # Python 3
   python -m http.server 8000

   # Node.js (npx)
   npx serve .
   ```

   然后访问 `http://localhost:8000`

## 编码说明

所有 HTML 文件均以 **UTF-8 (无 BOM)** 编码保存。如果浏览器显示乱码，请检查：

1. 浏览器编码是否被强制设为 GBK / GB2312
2. 本地服务器是否正确发送 `Content-Type: text/html; charset=utf-8` 头

每个 HTML 文件都包含 `<meta charset="UTF-8">`，标准浏览器应自动识别为 UTF-8。

## 设计要点

- **顶部导航**：固定吸顶，包含 Logo、7 个主导航项与「联系我们」按钮，移动端自动折叠为汉堡菜单。
- **统一页脚**：每个页面共享同样的页脚组件，包含品牌、产品、资源、公司、联系方式 5 列。
- **图片资源**：全部为本地 SVG 矢量图，体积小、清晰度高，无需联网依赖。
- **响应式**：在桌面、平板、手机上都有良好显示效果，关键断点为 1024px 和 768px。
- **可访问性**：使用语义化标签、`alt` 描述、对比度符合 WCAG AA。

## 内容来源

| 页面 | 内容参考 |
|---|---|
| 生物云计算 | [基因学苑生物云平台使用说明（2026版）](https://my.feishu.cn/wiki/DLQfwk5cdiYHMbkTB9kczLDPn4g) |
| AI+生物信息 | [《驯龙高手：利用AI辅助生物信息分析》课程介绍](https://my.feishu.cn/wiki/BXsMwQAHniLLkvkDdW7cDfqqnQI) |
| 视频课程 | [基因学苑生物信息课程简介](https://my.feishu.cn/wiki/Z9pHwlsQ5iAHv4kCxAncYkL2nog) |
| 关于我们 | http://www.tongyuangene.com/about.html |

## 联系方式

- **公司**：青岛同源基因科技有限责任公司
- **网址**：[www.tongyuangene.com](http://www.tongyuangene.com)
- **邮箱**：genomics@outlook.com
- **地址**：山东省青岛市高新区秀园路 1 号科创慧谷（青岛）科技园 D-2-264 室

---

© 2026 青岛同源基因科技有限责任公司 版权所有