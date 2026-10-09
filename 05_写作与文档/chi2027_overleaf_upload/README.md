# CHI 2027 Overleaf 项目 — 上传与使用说明

> 生成日期：2026-08-02　|　状态：可直接上传编译

## 一、这是什么

一个**自包含**的 CHI 2027 论文 Overleaf 项目：已内置 ACM 官方模板
（`acmart.cls` + `ACM-Reference-Format.bst`），**无需先在 Overleaf
选模板**，直接上传本 zip 即可编译。

## 二、文件清单（6 个文件）

| 文件 | 作用 | 状态 |
|:---|:---|:---|
| `main.tex` | 论文主文件（含完整大纲） | ✅ 大纲已写好，正文待填 |
| `relatedwork.tex` | Related Work 章节 | ✅ 成稿（中文，待译英） |
| `references.bib` | 参考文献库（22 条） | ✅ 全部经 Crossref 核验，零幻觉引用 |
| `acmart.cls` | ACM 官方模板类 | ✅ 官方原版 |
| `ACM-Reference-Format.bst` | 参考文献样式 | ✅ 官方原版 |
| `README_上传说明.md` | 本文档 | ✅ |

## 三、上传步骤（2 种方式任选）

**方式 A（推荐）：直接上传 zip**
1. Overleaf 首页 → **New Project → Upload Project** → 选择本 zip 包。
2. 上传后点开 `main.tex`，**Menu → Compiler** 选择 **XeLaTeX**。
3. 点击 **Recompile**，编译通过即生成 PDF 预览。

**方式 B：手动建项目再覆盖**
1. 新建项目时选择 CHI 官方模板（模板库搜 "ACM CHI" 或 "acmart"）。
2. 用本包内的 `main.tex` / `relatedwork.tex` / `references.bib`
   覆盖同名文件（模板自带的 `sigconf.tex` 等可删）。
3. 同上选 XeLaTeX 编译。

## 四、编译环境说明

- 当前 relatedwork.tex 为**中文草稿**，需 **XeLaTeX** + 中文字体
  （`main.tex` 已配置 `xeCJK` + `Noto Serif CJK SC`，Overleaf 预装）。
- 若报字体缺失：把 `main.tex` 里的 `\setCJKmainfont{Noto Serif CJK SC}`
  改为 `\setCJKmainfont{FandolSong}`（Overleaf 一定可用）。
- **全部翻译成英文后**，可将编译器切回 pdfLaTeX，并把
  `\usepackage{xeCJK}` 一行注释掉，速度更快。

## 五、当前内容状态

- ✅ **Related Work**：四条脉络完整（沉浸式新闻 / 具身与共情 /
  弱势群体 VR / Gap \& Contribution），22 个引用与 bib 一一对应
  （已程序校验：0 缺失、0 冗余）。
- ✅ **大纲**：Introduction / Method / Results / Discussion / Conclusion
  各节结构已写好（含建议段落与素材指引）。
- ⏳ **待办**：各节正文填充；relatedwork.tex 翻译成英文。

## 六、引用核验记录（2026-08-02，防幻觉引用）

| 事项 | 处理 |
|:---|:---|
| `ahn2013embodied` / `ahn2014short` | 原不在文献总表，已核实真实存在并补齐（Media Psychology 2013 / Computers in Human Behavior 2014） |
| `legacysphere2024` | 已核实（Shen, McGrenere \& Yoon, CHI '24, DOI 10.1145/3613904.3641923） |
| `vrscoping2024` | 已核实（Trevena, Paay \& McDonald, Virtual Reality 28(2):80, 2024） |
| `cultivating2024` | 成稿 key 写作 `cultivation2024`，统一为 `cultivating2024`（Hadjipanayi et al., PUC 28:507--519） |
| **Shocking Realities** | 出处修正：实际是 **DIS 2025**（非 CHI 2025），DOI 10.1145/3715336.3735809 |
| **An Equitable Experience?** | 出处修正：实际是 **ACM TACCESS 18(4)** 期刊（非 CHI 2025），DOI 10.1145/3770755 |
| **Feeling the News?** | 出处修正：实际发表于 **Digital Journalism 11(1):39--60**（非 Journalism Practice） |

## 七、下一步（写作线）

1. 上传并编译通过（今天即可）。
2. 在 Overleaf 上把 relatedwork.tex 逐段翻译成英文
   （建议先翻 2.4 Gap/Contribution，最重要）。
3. 数据筛选定稿后，用
   `docs/人机协作筛选_方法贡献记录.md` 与
   `docs/筛选方案对比_给老师汇报.md` 中的中英对照素材填 Method / Results。
