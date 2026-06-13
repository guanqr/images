# 更新日志

## v0.7.1 (2026-06-13)

### 修复
- **OSS 增量上传修复**：`sync_new_photos()` 改为基于实际处理文件列表判断上传，而非时间戳比较。`batch_process()` 返回本次处理过的文件名，传入 `sync_new_photos()` 的 `force_files` 参数，仅这些文件上传覆盖，其余跳过。

### 变更
- `batch_process()` — 返回 `processed_files` 列表
- `sync_new_photos()` — 新增 `force_files` 参数，替代不可靠的 mtime vs OSS last_modified 时间戳比较

---

## v0.7.0 (2026-06-13)

### 变更
- **目录重构**：源代码移至 `src/`，辅助脚本移至 `scripts/`
- 新增 `run.py` 作为根目录入口（`python run.py`）
- 所有 `__file__` 路径上移一级（`../fonts`、`../oss_config.json` 等）

---

## v0.6.0 (2026-06-13)

### 新增
- `oss_utils.py` — 阿里云 OSS 上传模块，处理完成后自动同步新图片到云端
- `oss_config.example.json` — OSS 凭证模板，真实凭证文件 `oss_config.json` 已 gitignore
- 支持配置文件 + 环境变量双重读取凭证

### 变更
- `main.py` — 处理完成后自动调用 `sync_new_photos()`
- CLAUDE.md — 补充 OSS 模块架构说明
- README.md — 补充阿里云 OSS 配置完整教程

---

## v0.5.0 (2026-06-13)

### 新增
- `exif_utils.py` — EXIF 信息提取（`get_exif_info()`, `get_year()`）
- `toml_utils.py` — TOML 读写与排序（`parse_toml_entries()`, `write_toml()`）
- `watermark.py` — 水印生成与单张图片处理（`get_region_brightness()`, `add_watermark()`, `process_image()`）

### 变更
- `main.py` — 从 290 行缩减至 ~80 行，仅保留入口与 `batch_process()` 调度逻辑

---

## v0.4.0 (2026-06-13)

### 新增
- `photo.toml` 自动更新：新增照片自动追加条目，EXIF 参数（focus/iso/aperture/shutter/time）自动填入
- 手动字段（alt/category/place/location/description）留空
- TOML 按 `time` 升序排序写入，无时间排最后

### 变更
- `get_photo_year()` → `get_exif_info()`，一次提取全部 EXIF 参数
- `parse_toml_entries()` + `write_toml()` 替代简单的追加逻辑
- 已存在条目的手动编辑内容完整保留，不会被覆盖

---

## v0.3.0 (2026-06-13)

### 新增
- 增量处理：比较输入/输出文件修改时间，未变化照片自动跳过
- 处理完成后输出统计：`📊 本次处理 X 张，跳过 Y 张（未变化）`

---

## v0.2.0 (2026-06-13)

### 新增
- 字体自动下载脚本 `download_font.py`（从 Google Fonts 获取 NotoSans-Bold.ttf）
- `.gitignore` — 忽略 `original_photos/`、`fonts/`、`__pycache__/`
- `README.md` — 使用说明

### 变更
- 所有路径改为基于 `os.path.dirname(__file__)` 的相对路径
- 输入目录：`original_photos/`
- 输出目录：`output_photos/`（自动创建）
- 字体路径：`fonts/NotoSans-Bold.ttf`

---

## v0.1.0 (2026-06-13)

### 初始版本
- `main.py` — 单文件批处理脚本
- 缩放长边至 1920px
- `Guanqr Photography @ 年份` 底部居中水印，颜色自适应明暗
- JPEG 压缩至 400KB 以内
- EXIF `DateTimeOriginal` 自动提取拍摄年份
- Windows 控制台 UTF-8 乱码修复
- 新旧 Pillow API 兼容
