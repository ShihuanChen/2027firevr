"""打「方法审查包」：保持仓库相对路径的裁剪副本 + 审查说明，供外部 AI/审稿人核方法。

与 pack_handoff.py 的区别：
  交接包按「读的顺序」重排，给人接手用；
  审查包保持仓库结构，脚本解压即可直接跑（脚本里的相对路径依赖这个结构）。

用法：
  python 06_工作流产物/pack_review.py
输出：仓库根 2027firevr_方法审查_20261023.zip
"""
import os
import shutil
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = '2027firevr_方法审查_20261023'
ZIP = os.path.join(REPO, NAME + '.zip')

# (来源相对路径, 是否整目录)；保持原路径，脚本才能直接运行
ITEMS = [
    '00_核心交付',
    '04_3D与VR场景',
    '05_编码包',
    '06_工作流产物/第18轮_三模型全量编码_20261022',
    'README.md',
]
# 05_编码包 里这三个是中间产物，不进包
DENY = {'_work', '_archive', '_tmp', '__pycache__', '.DS_Store'}

INTRO = """# 方法审查包

这份包是**仓库的裁剪副本**，目录路径与仓库一致——因为包内脚本用相对路径找数据，重排目录会让它们跑不起来。

## 先读这两份

1. `00_核心交付/20_方法审查说明_20261023.md` —— 方法、参数、结果、已知缺陷、复核命令，以及请重点审的六件事。
2. `00_核心交付/15_一致性初跑_78条.md` —— 一致性的逐条读法与英文段落。

## 想直接验数

```bash
cd 06_工作流产物/第18轮_三模型全量编码_20261022
python merge_and_kappa.py opus sonnet   # 离线复算三张 κ 表，不需要 API
python _selftest.py                     # 17 项自测
```

## 包里有什么

| 目录 | 内容 |
|---|---|
| `00_核心交付/` | 28 份：审查说明、交付清单、问与答、六轴 34 档、Codebook、验证报告、PRISMA 溯源、三张图（pdf+png）、抽检包、一致性、编码结果表、补搜候选 |
| `05_编码包/` | 106 篇正文输入包、103 起事件主表、单条编码提示词、数据自洽检查脚本（已剔除中间产物 `_work/_archive/_tmp`） |
| `06_工作流产物/第18轮_三模型全量编码_20261022/` | 跑批与统计脚本、`结果/`（逐字段·逐档·轴级 κ）、`_out/`（三模型原始返回，含证据引句） |
| `04_3D与VR场景/` | VR 复现场景与工程路线 |

未包含：`02_语料与标注/`（8,180 条原始库，5.6 MB，可由脚本重抓）、`08_交付物备份/`、`09_会议后行动/`、`10_过程归档/`。
"""


def main():
    tmp = tempfile.mkdtemp(prefix='review_')
    root = os.path.join(tmp, NAME)
    try:
        os.makedirs(root)
        open(os.path.join(root, '00_审查包说明.md'), 'w', encoding='utf-8').write(INTRO)

        n_file = 0
        for rel in ITEMS:
            src = os.path.join(REPO, rel)
            dst = os.path.join(root, rel)
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                n_file += 1
                continue
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*DENY))
            n_file += sum(len(fs) for _, _, fs in os.walk(dst))

        if os.path.exists(ZIP):
            os.remove(ZIP)
        with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for dp, dns, fns in os.walk(root):
                dns[:] = [d for d in dns if d not in DENY]
                for fn in sorted(fns):
                    if fn in DENY or fn.endswith('.pyc'):
                        continue
                    fp = os.path.join(dp, fn)
                    z.write(fp, os.path.relpath(fp, tmp))

        total = len(zipfile.ZipFile(ZIP).namelist())
        print(f'审查包：{total} 个条目（{n_file} 个文件），{os.path.getsize(ZIP)/1e6:.1f} MB')
        print(ZIP)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
