"""重打交接包：从本仓库取文件，生成 2027firevr_交接_20261023.zip 到仓库根。

什么时候跑：仓库里任何文件改过之后。跑完提交 zip，交接方拿到的就是最新版。

用法：
  python 06_工作流产物/pack_handoff.py

包内结构与仓库的对应关系：
  00_先读我.md          ← 00_核心交付/19_交接包说明.md（改名）
  迁移提示词.txt         ← 00_核心交付/09_交付话术与迁移提示词.md 的第一段代码块
  01_核心交付/           ← 00_核心交付/（不含 18 号，它已升为根目录入口）
  02_编码包/             ← 05_编码包/ 的六个文件
  03_跑批与结果/         ← 第18轮 的脚本、README、结果/、_out/
  04_VR场景/             ← 04_3D与VR场景/ 的三个文件
  05_原始数据索引/       ← 本脚本内置的一句话说明
  06_直接打标/           ← 07_直接打标_20261023/（把文章贴给网页 AI 打标的批次与脚本）
"""
import os
import re
import shutil
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_NAME = '2027firevr_交接_20261023'
ZIP = os.path.join(REPO, PKG_NAME + '.zip')

CORE_SRC = os.path.join(REPO, '00_核心交付')
ENTRY = os.path.join(CORE_SRC, '19_交接包说明.md')
TALK = os.path.join(CORE_SRC, '09_交付话术与迁移提示词.md')

CODING_FILES = ['输入包_编码集v4.csv', '编码集v4_事件.csv', '提示词与交付_v4_单条.md',
                'check_consistency.py', '合并与一致性.py', '结果_模型DeepSeek.jsonl']
PIPE_DIR = os.path.join(REPO, '06_工作流产物', '第18轮_三模型全量编码_20261022')
PIPE_FILES = ['run_models.py', 'merge_and_kappa.py', 'merge_lib.py', '_selftest.py',
              'recover_ids.py', 'make_prisma_v2.py', 'make_figs.py',
              'build_deliverable.py', 'README.md']
PIPE_DIRS = ['结果', '_out']
VR_DIR = os.path.join(REPO, '04_3D与VR场景')
VR_FILES = ['14_VR复现场景_四案带依据_20261022.md', 'VR开发路线_v1_20261022.md', 'VR_mapping_v0.2.md']
MANUAL_DIR = os.path.join(REPO, '07_直接打标_20261023')

SKIP = {'__pycache__', '.DS_Store', 'run.log', '19_交接包说明.md'}

RAW_NOTE = """# 原始数据不在包内

包内只放可交接的分析层。8,180 条原始库与打标表体积 5.6 MB、属于可重抓的中间产物，留在仓库：

| 文件（仓库路径） | 内容 |
|---|---|
| `02_语料与标注/data/高层火灾_补充正文_v2_20260701.csv` | 全量库，含 811 条可回抓正文 |
| `02_语料与标注/data/高层火灾新闻可用精选_20260701.csv` | 1,027 去重候选池 |
| `02_语料与标注/data/高层火灾_第二轮打标_20260701.csv` | 打标记录 |
| `02_语料与标注/data/场景还原指标_打标_20260701.csv` | 场景还原维度打标 |

分析层已全在包内：`02_编码包/输入包_编码集v4.csv` 是 106 篇编码输入（标题、正文、URL、事件组 ID），`编码集v4_事件.csv` 是 103 起事件主表。只做分析或写作不需要原始库。

要复现筛选漏斗（8,180 → 6,666 → 1,443 → 1,027 → 291 → 125）才需要上表第一行；每一跳的出处见 `01_核心交付/07_PRISMA_2020_数字溯源.md`。
"""


def extract_prompt():
    s = open(TALK, encoding='utf-8').read()
    i = s.index('## B1 ')
    j = s.index('```', i) + 3
    k = s.index('```', j)
    return s[j:k].strip() + '\n'


def main():
    tmp = tempfile.mkdtemp(prefix='handoff_')
    pkg = os.path.join(tmp, PKG_NAME)
    try:
        os.makedirs(pkg)
        shutil.copy2(ENTRY, os.path.join(pkg, '00_先读我.md'))
        open(os.path.join(pkg, '迁移提示词.txt'), 'w', encoding='utf-8').write(extract_prompt())

        d = os.path.join(pkg, '01_核心交付')
        os.makedirs(d)
        n = 0
        for f in sorted(os.listdir(CORE_SRC)):
            if f in SKIP or not os.path.isfile(os.path.join(CORE_SRC, f)):
                continue
            shutil.copy2(os.path.join(CORE_SRC, f), os.path.join(d, f))
            n += 1

        d = os.path.join(pkg, '02_编码包')
        os.makedirs(d)
        for f in CODING_FILES:
            shutil.copy2(os.path.join(REPO, '05_编码包', f), os.path.join(d, f))
            n += 1

        d = os.path.join(pkg, '03_跑批与结果')
        os.makedirs(d)
        for f in PIPE_FILES:
            shutil.copy2(os.path.join(PIPE_DIR, f), os.path.join(d, f))
            n += 1
        for sub in PIPE_DIRS:
            shutil.copytree(os.path.join(PIPE_DIR, sub), os.path.join(d, sub),
                            ignore=shutil.ignore_patterns(*SKIP))

        d = os.path.join(pkg, '04_VR场景')
        os.makedirs(d)
        for f in VR_FILES:
            shutil.copy2(os.path.join(VR_DIR, f), os.path.join(d, f))
            n += 1

        d = os.path.join(pkg, '06_直接打标')
        # 结果/（三路 jsonl + 一致性表 + 合并结果）随包带走；粘贴/ 原始回复不入包
        shutil.copytree(MANUAL_DIR, d, ignore=shutil.ignore_patterns(*SKIP, '粘贴'))
        # run_models.py 是 03_把回复转成结果.py 的依赖（复用同一套字段白名单与
        # 归一化），仓库里它在 第18轮 子目录，包内目录结构不同，故复制一份过来
        shutil.copy2(os.path.join(PIPE_DIR, 'run_models.py'),
                     os.path.join(d, 'run_models.py'))

        d = os.path.join(pkg, '05_原始数据索引')
        os.makedirs(d)
        open(os.path.join(d, 'README.md'), 'w', encoding='utf-8').write(RAW_NOTE)

        if os.path.exists(ZIP):
            os.remove(ZIP)
        with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for dp, dns, fns in os.walk(pkg):
                dns[:] = [x for x in dns if x not in SKIP]
                for fn in sorted(fns):
                    if fn in SKIP or fn.endswith('.pyc'):
                        continue
                    fp = os.path.join(dp, fn)
                    z.write(fp, os.path.relpath(fp, tmp))

        total = len(zipfile.ZipFile(ZIP).namelist())
        print(f'交接包已生成：{total} 个条目，{os.path.getsize(ZIP)/1e6:.1f} MB')
        print(ZIP)
        print(f'（其中 01_核心交付 来源文件 {n - len(CODING_FILES) - len(PIPE_FILES) - len(VR_FILES)} 份）')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
