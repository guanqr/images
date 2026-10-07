# 更新日志

## v0.8.0 (2026-10-07)

### 新增
- `exif_utils.py` — EXIF 提取扩展：新增 `camera`（Model 优先，缺品牌补 Make）、`lens`（LensModel/LensMake）、原始像素 `width`/`height`
- `backfill_camera_lens.py` — 一次性回填脚本，从原始照片读取相机/镜头信息写入 `photo.toml`，不做图片处理与 OSS 上传
- `toml_utils.py` — 支持 `featured` 精选字段（仅 `true` 时写出）

### 变更
- `exif_utils.py` / `toml_utils.py` — 读写两侧清洗控制字符（EXIF 可能携带末尾 NUL 等，否则生成非法 TOML）
- `toml_utils.py` — FIELDS 扩展 `width`/`height`/`camera`/`lens`
- `main.py` — 新条目自动填入 `camera`/`lens`/`width`/`height`；历史条目缺宽高时从 output_photos 读取像素尺寸回填
- `photo.toml` — 74 条历史记录回填相机/镜头/宽高，17 条添加 `featured` 标记，新增 27 张照片
- 分类重命名：`landscape`/`city`/`countryside` 统一为 `scenery`
- `output_photos/` — 新增 37 张处理结果，14 张重新生成

---

## v0.7.2 (2026-06-15)

### 新增
- `photo.toml` 支持组照元数据字段 `series`（组照名称）和 `is_cover`（是否为组照封面）
- 默认不自动生成这两个字段，用户手动添加后 `write_toml()` 保留不覆盖
- `parse_toml_entries()` 支持解析非引号值（`true`/`false` 布尔值）

---

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
