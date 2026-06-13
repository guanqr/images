# 摄影作品批量处理工具 — 构建指南

## 项目概述

一个 Python 批处理脚本，为摄影作品自动添加水印、缩放尺寸、压缩输出。处理流程：读取原始图片 → 缩放长边至目标像素 → 底部居中加水印（自动选色+年份） → JPEG 压缩至目标大小。

## 核心架构

```
run.py                   # 根目录入口
src/
├── main.py              # 入口 + batch_process() 调度逻辑，返回已处理文件列表
├── exif_utils.py        # get_exif_info(), get_year()
├── toml_utils.py        # parse_toml_entries(), write_toml()
├── watermark.py         # get_region_brightness(), add_watermark(), process_image()
└── oss_utils.py         # create_bucket_from_config(), sync_new_photos(force_files)
scripts/
└── download_font.py     # Google Fonts 字体下载
```

## 关键设计决策

### 1. 水印透明度用独立图层
不要直接在原图上 `draw.text()`，而是新建 `Image.new("RGBA", ...)` 透明图层，画水印后用 `Image.alpha_composite()` 合并。这样水印透明度（opacity）完全可控，不会和图片像素意外混合。

### 2. 水印颜色根据底部明暗自动选择
截取图片底部 100px 区域，转为灰度计算平均亮度。亮度 > 127（偏亮）用黑色水印，否则用白色水印。这解决了水印在各类照片上都清晰可见的问题。

### 3. 年份从 EXIF 自动提取
优先读取 `DateTimeOriginal`（原始拍摄时间），没有则回退到 `DateTime`（文件修改时间）。取前 4 位作为年份，拼接到水印文字末尾：`Guanqr Photography @ 2025`。

### 4. 压缩循环降质量
从 quality=95 开始，每次降 5，直到 JPEG 大小 ≤ 400KB 或 quality 降到 10。用 `BytesIO` 在内存中完成，不写临时文件。

### 5. 自动更新 photo.toml
处理每张照片时，检查其 `src` 是否已存在于 TOML 中。不存在则追加新 `[[photo]]` 条目：
- EXIF 字段（focus, iso, aperture, shutter, time）自动填入
- 手动编辑字段（alt, category, place, location）留空，等待用户自行填写
- 用正则 `^src\s*=\s*"(.+)"` 快速解析已有条目，无需第三方 TOML 库
- `src` 路径约定为 `/images/photos/<filename>`，与前端路由对齐

### 6. 增量处理（避免重复工作）
`batch_process()` 比较输入和输出文件的修改时间（`os.path.getmtime`）：
- 输出不存在 → 处理
- 输出存在且 `output_mtime >= input_mtime` → 跳过
- 输出存在但 `input_mtime > output_mtime` → 重新处理

这是最简单的增量策略，不需要哈希缓存文件。

### 7. 字体独立下载脚本
字体文件不提交到 Git 仓库。提供 `download_font.py` 从 Google Fonts 自动下载：
- 请求 `https://fonts.google.com/download?family=Noto+Sans`（返回 ZIP）
- 在 ZIP 中查找匹配 `*Bold*.ttf` 的文件
- 解压到 `fonts/` 目录

使用 `download_font.py` 而非 shell 脚本的好处：跨平台，且与主程序共享 Python 生态。

### 8. TOML 按时间排序
`write_toml()` 按 `time` 字段升序重写整个文件，而非简单追加。`parse_toml_entries()` 完整保留所有手动编辑字段，新增照片插入到正确的时间位置。

### 9. OSS 凭证独立配置文件
`oss_config.json` 独立于代码仓库（已 gitignore），通过 `oss_config.example.json` 提供模板。`create_bucket_from_config()` 优先读配置文件，回退到环境变量。

### 10. OSS 增量上传（避免重复工作）
`batch_process()` 返回本次实际处理过的文件名列表（`processed_files`），传给 `sync_new_photos()` 的 `force_files` 参数：
- 在 `force_files` 中的文件 → 始终上传覆盖 OSS 同名对象
- 不在 `force_files` 中但 OSS 上不存在 → 上传（兜底首次上传）
- 不在 `force_files` 中且 OSS 上已存在 → 跳过

这比时间戳比较（本地 mtime vs OSS last_modified）更可靠，因为本地和云端的时间基准可能不一致。

## 依赖

```
Pillow  # PIL: Image, ImageDraw, ImageFont, ExifTags
oss2    # 阿里云 OSS SDK（可选，仅上传时需要）
```

标准库：`os`, `sys`, `io.BytesIO`, `urllib.request`, `zipfile`, `json`, `re`, `fractions`

## 目录结构约定

```
项目根目录/
├── run.py                   # 入口（python run.py）
├── src/                     # 源代码
│   ├── main.py              # 入口与调度
│   ├── exif_utils.py        # EXIF 提取
│   ├── toml_utils.py        # TOML 读写排序
│   ├── watermark.py         # 水印与图片处理
│   └── oss_utils.py         # OSS 上传工具
├── scripts/                 # 辅助脚本
│   └── download_font.py     # 字体下载
├── oss_config.example.json  # OSS 凭证模板
├── fonts/                   # 字体目录（gitignore）
│   └── NotoSans-Bold.ttf
├── original_photos/         # 原始照片（gitignore）
├── output_photos/           # 处理后输出（gitignore，自动创建）
├── photo.toml               # 照片元数据
├── .gitignore
└── README.md
```

所有路径均使用 `os.path.dirname(__file__)` 相对定位，保证项目可迁移。

## 兼容性处理

- **Windows 控制台乱码**：`sys.stdout` 重新包装为 UTF-8 writer
- **新旧 Pillow API**：`textbbox`（新）/ `textsize`（旧）fallback；`get_flattened_data` / `getdata` fallback
- **字体加载失败**：`ImageFont.load_default()` 兜底

## 扩展方向

如需增强，可沿以下方向：
- **水印位置**：可改为右下角、平铺水印等
- **多字体回退**：尝试多个字体路径
- **并发处理**：`concurrent.futures.ThreadPoolExecutor` 加速批量处理
- **配置文件**：用 JSON/YAML 替代硬编码的水印文字、目标尺寸、压缩上限
- **内容哈希**：用文件哈希（SHA256）替代修改时间判断，更可靠
