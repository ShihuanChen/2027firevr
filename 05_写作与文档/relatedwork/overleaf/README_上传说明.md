# CHI 2027 Overleaf 项目 — 上传与使用说明

> 生成日期：2026-08-02　|　状态：可上传编译

## 一、文件清单（本目录 3 个文件）

| 文件 | 作用 | 说明 |
|:---|:---|:---|
| `main.tex` | 论文主文件（骨架） | acmart 模板 + 各章节占位，已启用匿名模式 |
| `relatedwork.tex` | Related Work 章节 | 中文成稿转 LaTeX，**待翻译成英文** |
| `references.bib` | 参考文献库 | 22 条，全部经 Crossref 核验，零幻觉引用 |

## 二、上传步骤

1. 登录 Overleaf（用朱倩提供的会员账号），新建项目时选择 **CHI 官方模板**（模板库搜 "ACM CHI" 或 "acmart"），得到一个带 `acmart.cls` 的项目。
2. 把本目录的 `main.tex`、`relatedwork.tex`、`references.bib` 三个文件**上传覆盖**同名文件（或直接拖入覆盖）。
3. 菜单 **Menu → Compiler** 选择 **XeLaTeX**（因为 relatedwork.tex 还是中文，需要 xeCJK；全部翻成英文后可切回 pdfLaTeX）。
4. 点击 Recompile。若编译报字体缺失，把 `main.tex` 里的 `\setCJKmainfont{...}` 改成 Overleaf 中可用的中文字体（如 `Noto Serif CJK SC` 通常已预装）。

## 三、当前内容状态

- ✅ **Related Work**：四条脉络完整（沉浸式新闻 / 具身与共情 / 弱势群体 VR / Gap & Contribution），22 个引用与 bib 一一对应。
- ⏳ **待办**：Introduction / Method / Results / Discussion / Conclusion 均为 TODO 占位。
- ⚠️ **中文待翻译**：relatedwork.tex 保留中文原文，建议在 Overleaf 上逐段协作翻译成英文（保留修改痕迹方便审阅）。

## 四、引用核验记录（2026-08-02，防止幻觉引用）

| 事项 | 处理 |
|:---|:---|
| `ahn2013embodied` / `ahn2014short` | 原不在文献总表，已核实真实存在并补齐（Media Psychology 2013 / Computers in Human Behavior 2014） |
| `legacysphere2024` | 已核实（Shen, McGrenere & Yoon, CHI '24, DOI 10.1145/3613904.3641923） |
| `vrscoping2024` | 已核实（Trevena, Paay & McDonald, Virtual Reality 28(2):80, 2024） |
| `cultivating2024` | 成稿 key 写作 `cultivation2024`，统一为 `cultivating2024`（Hadjipanayi et al., PUC 28:507–519） |
| **Shocking Realities** | ⚠️ 出处修正：实际是 **DIS 2025**（Designing Interactive Systems），成稿原写 CHI 2025 |
| **An Equitable Experience?** | ⚠️ 出处修正：实际是 **ACM Trans. Accessible Computing 18(4)** 期刊论文，成稿原写 CHI 2025 |
| **Feeling the News?** | ⚠️ 出处修正：实际发表于 **Digital Journalism 11(1):39–60**（非 Journalism Practice） |

> 第 5-7 行三处 venue 已在 `relatedwork.tex` 中同步修正，无需手动改。

## 五、下一步（写作线）

1. 上传并编译通过（今天即可）。
2. 在 Overleaf 上把 relatedwork.tex 逐段翻译成英文（可先翻 2.4 Gap/Contribution，因为它最重要）。
3. 数据筛选定稿后，用 `docs/人机协作筛选_方法贡献记录.md` 与 `docs/筛选方案对比_给老师汇报.md` 中的中英对照素材填 Method / Results。
