# 科研图鉴 · Figure Atlas 2026

一个用于探索科研绘图表达方式的静态网站，整理人工选出的 **ICLR、CVPR、ACL、EMNLP 2026** 图片、主副类别和论文信息。

**[打开网站](https://23whguo.github.io/scientific-figure-gallery-2026/)** · [数据目录](data/figures.json) · [整理方法](docs/methodology.html) · [图片版权](IMAGES_POLICY.md)

| 会议 | 图片 |
|---|---:|
| ICLR 2026 | 1,017 |
| CVPR 2026 | 660 |
| ACL 2026 | 983 |
| EMNLP 2026 | 171 |
| 合计 | **2,831** |

共关联 **2,117 篇论文**。此次发布只包含原图、类别和论文资料，**不包含 PPT、TeX、模型密钥或本地评审结果**。

## 功能

- 搜索标题、作者、图注、摘要和关键词。
- 按会议、年份、主副类别、主会/Findings、已有录取类型筛选；按会议、标题、类别排序或随机浏览。
- 响应式瀑布流；每页 100 张、分页跳转、懒加载和相邻页面缩略图预取。
- 大图对话框、前后切图、缩放拖动、原图下载、原论文/PDF/arXiv/项目链接。
- 浏览器本地收藏、灵感笔记、主副类别修正；JSON 备份/导入、筛选结果导出、旧分类 JSON 兼容导入。
- 引用/BibTeX 复制、带筛选条件和图片 ID 的分享链接。
- 中英文界面、明暗主题、布局密度切换、手机界面与键盘操作。

快捷键：`/` 搜索，`←` / `→` 大图切换，`+` / `-` 缩放，`f` 收藏，`Esc` 关闭大图。

## 本地运行

直接打开 `index.html`，或：

```sh
python -m http.server 8790 --bind 127.0.0.1
```

然后访问 http://127.0.0.1:8790/ 。零 npm 依赖、无需构建。字体无法联网时回退系统字体。收藏和个人分类在浏览器中保存，换设备或域名时用 JSON 备份迁移。

## 项目结构

```text
index.html                 图库入口
assets/app.js              搜索、筛选、大图、收藏、导入导出
assets/style.css           视觉样式与响应式布局
assets/figures.js           可直接离线打开的公开数据
data/figures.json           完整可追溯目录
data/catalog.json           分类表和统计
images/iclr/final/          ICLR 浏览图
images/iclr/thumbs/         ICLR 缩略图（其他会议同结构）
docs/                      来源、整理方法和说明
scripts/build_catalog.py   从已保存选择快照构建目录和 WebP
scripts/validate_catalog.py 公开产物完整性检查
tests/                     浏览器行为验证
.github/workflows/pages.yml GitHub Pages 自动部署
```

## 更新数据

本地构建脚本读取维护者原有选择和分类快照，校验原始预览哈希，排除 HF，并按 ID 合并 ICLR 论文资料。与图片版本匹配的已导出人工分类优先；其他记录使用 JEV/CLEF 主副类别。原数据不会被修改。

```sh
python -m pip install Pillow
python scripts/build_catalog.py
python scripts/validate_catalog.py
```

`build_catalog.py` 中的数据输入路径适用于当前维护环境，使用其他环境时请修改入口路径。发布产物不依赖这些路径。浏览器中的个人修改须导出后才能用于后续公开目录更新。

## GitHub Pages

仓库 Settings → Pages → Source 选 **GitHub Actions**，向 `main` 推送即自动校验并部署。该工作流只打包公开页面、图片、目录和说明，不部署构建环境或原始下载目录。

## 许可与致谢

网站代码使用 MIT 许可。论文图片和论文文字的权利属于原作者及出版者，并不因本站整理而统一变成 MIT 或 CC BY。使用图片时请核对原论文许可并注明来源；详见 [IMAGES_POLICY.md](IMAGES_POLICY.md)。

整理方式及图库功能参考 [qwdwqfwq/topconf-paper-figure-gallery](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)。网站界面和这四个会议的选图、类别目录独立整理。本站公开图库不需要 API；AI 绘图创作工具属于另一个功能范围。
