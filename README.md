# 摄影作品批量处理工具

自动为摄影作品添加水印、缩放尺寸、压缩输出，并从 EXIF 中提取拍摄参数写入 `photo.toml`。

## 目录结构

```
项目根目录/
├── main.py              # 入口与调度
├── exif_utils.py        # EXIF 信息提取
├── toml_utils.py        # photo.toml 读写排序
├── watermark.py             # 水印与图片处理
├── oss_utils.py             # OSS 上传工具
├── download_font.py         # 字体下载脚本
├── fonts/                   # 字体目录（自动下载）
│   └── NotoSans-Bold.ttf
├── original_photos/         # 原始照片（放这里）
├── output_photos/           # 处理后照片（自动生成）
├── photo.toml               # 照片元数据（自动补全）
├── oss_config.example.json  # OSS 凭证模板
├── .gitignore
└── README.md
```

## 准备工作

1. 安装 Python 3.x
2. 安装依赖并下载字体：

```bash
pip install Pillow oss2
python download_font.py
```

3. （可选）配置阿里云 OSS 环境变量，用于自动同步图片到云端（详见下方）
4. 将需要处理的 `.jpg` / `.jpeg` 照片放入 `original_photos/` 文件夹

## 使用方法

```bash
python main.py
```

## 阿里云 OSS 同步（可选）

如需将处理后的图片自动上传到阿里云 OSS，按以下步骤操作：

### 1. 开通 OSS 并创建 Bucket

1. 注册 [阿里云账号](https://www.aliyun.com/)
2. 进入 [OSS 控制台](https://oss.console.aliyun.com/)，点击「创建 Bucket」
3. Bucket 名称自定义（如 `my-photos`），地域选离你最近的
4. **读写权限**选择「公共读」（图片需要公开访问）

### 2. 获取 AccessKey

1. 进入 [RAM 访问控制](https://ram.console.aliyun.com/users) → 创建用户
2. 勾选「OpenAPI 调用访问」，创建后会得到 **AccessKey ID** 和 **AccessKey Secret**（Secret 只显示一次，立即保存）
3. 为该用户添加权限：`AliyunOSSFullAccess`

### 3. 配置 Bucket 跨域（可选，前端直接读取时需要）

在 Bucket 的「数据安全」→「跨域设置」中添加规则：
- 来源：`*`
- Methods：`GET`
- Headers：`*`

### 4. 配置凭证文件

复制模板文件并填入你的信息：

```bash
copy oss_config.example.json oss_config.json
```

编辑 `oss_config.json`：

```json
{
    "access_key_id": "你的AccessKey ID",
    "access_key_secret": "你的AccessKey Secret",
    "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
    "bucket_name": "my-photos"
}
```

> Endpoint 根据 Bucket 所在地域填写，如 `oss-cn-shanghai`、`oss-cn-beijing` 等。
> `oss_config.json` 已加入 `.gitignore`，不会被上传到 GitHub。

配置后，每次运行 `python main.py` 会自动将新图片上传到 OSS，上传路径为 `images/photos/<文件名>`，已存在的文件自动跳过。

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
