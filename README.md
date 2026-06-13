# 摄影作品批量处理工具

自动为摄影作品添加水印、缩放尺寸并压缩输出的批处理脚本。

## 目录结构

```
项目根目录/
├── main.py              # 主程序
├── fonts/               # 字体文件夹
│   └── NotoSans-Bold.ttf
├── original_photos/     # 原始照片（放这里）
└── output_photos/       # 处理后照片（自动生成）
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
- **水印**：底部居中添加 `Guanqr Photography @ 年份` 水印
  - 年份自动从 EXIF 中的 `DateTimeOriginal` 读取
  - 水印颜色根据底部区域明暗自动选择黑白
- **压缩**：输出 JPEG，大小控制在 400KB 以内

## 增量处理

只处理新增或发生变化的照片，未变化的照片自动跳过，避免重复工作。
