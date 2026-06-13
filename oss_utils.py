# -*- coding: utf-8 -*-
"""阿里云 OSS 上传工具"""
import os


def upload_to_oss(local_path, object_name, bucket):
    """上传单个文件到 OSS"""
    bucket.put_object_from_file(object_name, local_path)
    # 返回公开访问 URL
    return f"https://{bucket.bucket_name}.{bucket.endpoint.replace('https://', '')}/{object_name}"


def sync_new_photos(output_dir, bucket, oss_prefix="images/photos/"):
    """
    将 output_dir 中的新图片上传到 OSS。
    通过 OSS 上已有文件列表判断是否需要上传（避免重复覆盖）。
    """
    if not os.path.exists(output_dir):
        return

    # 获取 OSS 上已有文件集合
    existing = set()
    for obj in bucket.list_objects(prefix=oss_prefix).object_list:
        existing.add(obj.key)

    uploaded = 0
    skipped = 0
    for f in sorted(os.listdir(output_dir)):
        if not f.lower().endswith((".jpg", ".jpeg")):
            continue

        object_name = oss_prefix + f
        local_path = os.path.join(output_dir, f)

        if object_name in existing:
            skipped += 1
            continue

        url = upload_to_oss(local_path, object_name, bucket)
        print(f"☁️  已上传：{f}  →  {url}")
        uploaded += 1

    if uploaded or skipped:
        print(f"☁️  OSS 上传 {uploaded} 张，跳过 {skipped} 张（已存在）")


def create_bucket_from_config():
    """从 oss_config.json 读取凭证，不存在则尝试环境变量，均未配置返回 None"""
    import json
    import oss2

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oss_config.json")

    credentials = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                credentials = json.load(f)
        except Exception as e:
            print(f"⚠️  oss_config.json 解析失败: {e}")
            return None
    else:
        # 回退到环境变量
        credentials = {
            "access_key_id": os.environ.get("OSS_ACCESS_KEY_ID", ""),
            "access_key_secret": os.environ.get("OSS_ACCESS_KEY_SECRET", ""),
            "endpoint": os.environ.get("OSS_ENDPOINT", ""),
            "bucket_name": os.environ.get("OSS_BUCKET_NAME", ""),
        }

    access_key_id = credentials.get("access_key_id", "").strip()
    access_key_secret = credentials.get("access_key_secret", "").strip()
    endpoint = credentials.get("endpoint", "").strip()
    bucket_name = credentials.get("bucket_name", "").strip()

    if not all([access_key_id, access_key_secret, endpoint, bucket_name]):
        print("⚠️  未配置 OSS 凭证，跳过上传")
        print("   请复制 oss_config.example.json 为 oss_config.json 并填写你的凭证")
        return None

    auth = oss2.Auth(access_key_id, access_key_secret)
    return oss2.Bucket(auth, endpoint, bucket_name)
