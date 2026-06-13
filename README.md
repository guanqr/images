# 摄影作品批量处理工具

自动为摄影作品添加水印、缩放尺寸、压缩输出，并从 EXIF 中提取拍摄参数写入 `photo.toml`。

## 目录结构

```
项目根目录/
├── main.py              # 入口与调度
├── exif_utils.py        # EXIF 信息提取
├── toml_utils.py        # photo.toml 读写排序
├── watermark.py         # 水印与图片处理
├── download_font.py     # 字体下载脚本
├── fonts/               # 字体目录（自动下载）
│   └── NotoSans-Bold.ttf
├── original_photos/     # 原始照片（放这里）
├── output_photos/       # 处理后照片（自动生成）
├── photo.toml           # 照片元数据（自动补全）
├── .gitignore
└── README.md
```

## 准备工作

1. 安装 Python 3.x
2. 安装依赖并下载字体：

```bash
pip install Pillow
python download_font.py
```

3. 将需要处理的 `.jpg` / `.jpeg` 照片放入 `original_photos/` 文件夹

## 使用方法

```bash
python main.py
```

## 处理内容

- **缩放**：长边缩放至 1920px
- **水印**：`Guanqr Photography @ 年份` 底部居中
  - 年份自动从 EXIF `DateTimeOriginal` 读取
  - 颜色根据底部区域明暗自动选择黑白
- **压缩**：JPEG 质量循环递减，控制在 400KB 以内

## photo.toml 自动更新

每张新增照片会自动追加到 `photo.toml`，EXIF 拍摄参数自动填入，手动字段留空，按拍摄时间升序排列。已有条目的手动编辑内容不会被覆盖。

| 字段 | 来源 |
|------|------|
| focus / iso / aperture / shutter / time | EXIF 自动提取 |
| alt / category / place / location / description | 留空，手动填写 |

## 增量处理

只处理新增或发生变化的照片，未变化的自动跳过，避免重复工作。
