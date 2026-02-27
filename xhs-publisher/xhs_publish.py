#!/usr/bin/env python3
"""
小红书云端全自动发帖脚本 v2.0
支持：图文发帖（带图片）、纯文字发帖
无需浏览器，纯 HTTP + 签名算法
"""
import json
import hashlib
import time
import ctypes
import urllib.parse
import subprocess
import sys
import os
import argparse
from pathlib import Path

COOKIE_FILE = Path(__file__).parent.parent / 'credentials' / 'xhs_cookies.json'
HOST = "https://edith.xiaohongshu.com"
CREATOR_HOST = "https://creator.xiaohongshu.com"

# ===== 签名算法 =====

def h_encode(n):
    m = ""
    d = "A4NjFqYu5wPHsO0XTdDgMa2r1ZQocVte9UJBvk6/7=yRnhISGKblCWi+LpfE8xzm3"
    for i in range(0, 32, 3):
        o = ord(n[i])
        g = ord(n[i + 1]) if i + 1 < 32 else 0
        hh = ord(n[i + 2]) if i + 2 < 32 else 0
        x = ((o & 3) << 4) | (g >> 4)
        p = ((15 & g) << 2) | (hh >> 6)
        v = o >> 2
        b = hh & 63 if hh else 64
        if not g:
            p = b = 64
        m += d[v] + d[x] + d[p] + d[b]
    return m


def mrc(e):
    ie = [
        0, 1996959894, 3993919788, 2567524794, 124634137, 1886057615,
        3915621685, 2657392035, 249268274, 2044508324, 3772115230, 2547177864,
        162941995, 2125561021, 3887607047, 2428444049, 498536548, 1789927666,
        4089016648, 2227061214, 450548861, 1843258603, 4107580753, 2211677639,
        325883990, 1684777152, 4251122042, 2321926636, 335633487, 1661365465,
        4195302755, 2366115317, 997073096, 1281953886, 3579855332, 2724688242,
        1006888145, 1258607687, 3524101629, 2768942443, 901097722, 1119000684,
        3686517206, 2898065728, 853044451, 1172266101, 3705015759, 2882616665,
        651767980, 1373503546, 3369554304, 3218104598, 565507253, 1454621731,
        3485111705, 3099436303, 671266974, 1594198024, 3322730930, 2970347812,
        795835527, 1483230225, 3244367275, 3060149565,
    ] + [0] * (256 - 64)
    o = -1

    def right_without_sign(num, bit=0):
        val = ctypes.c_uint32(num).value >> bit
        MAX32INT = 4294967295
        return (val + (MAX32INT + 1)) % (2 * (MAX32INT + 1)) - MAX32INT - 1

    for n in range(min(57, len(e))):
        o = ie[(o & 255) ^ ord(e[n])] ^ right_without_sign(o, 8)
    return o ^ -1 ^ 3988292384


def encode_utf8(e):
    b = []
    m = urllib.parse.quote(e, safe='~()*!.')
    w = 0
    while w < len(m):
        T = m[w]
        if T == "%":
            S = int(m[w + 1] + m[w + 2], 16)
            b.append(S)
            w += 2
        else:
            b.append(ord(T[0]))
            w += 1
    return b


_lookup = [
    "Z","m","s","e","r","b","B","o","H","Q","t","N","P","+","w","O",
    "c","z","a","/","L","p","n","g","G","8","y","J","q","4","2","K","W",
    "Y","j","0","D","S","f","d","i","k","x","3","V","T","1","6","I","l",
    "U","A","F","M","9","7","h","E","C","v","u","R","X","5"
]

def b64_encode(e):
    P = len(e)
    W = P % 3
    U = []
    z = 16383
    H = 0
    Z = P - W
    while H < Z:
        chunk = []
        for b in range(H, Z if H + z > Z else H + z, 3):
            n = (16711680 & (e[b] << 16)) + ((e[b + 1] << 8) & 65280) + (e[b + 2] & 255)
            chunk.append(_lookup[63 & (n >> 18)] + _lookup[63 & (n >> 12)] + _lookup[(n >> 6) & 63] + _lookup[n & 63])
        U.append(''.join(chunk))
        H += z
    if 1 == W:
        F = e[P - 1]
        U.append(_lookup[F >> 2] + _lookup[(F << 4) & 63] + "==")
    elif 2 == W:
        F = (e[P - 2] << 8) + e[P - 1]
        U.append(_lookup[F >> 10] + _lookup[63 & (F >> 4)] + _lookup[(F << 2) & 63] + "=")
    return "".join(U)


def sign(uri, data=None, a1="", b1="", ctime=None):
    v = int(round(time.time() * 1000) if not ctime else ctime)
    raw_str = f"{v}test{uri}{json.dumps(data, separators=(',', ':'), ensure_ascii=False) if isinstance(data, dict) else ''}"
    md5_str = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
    x_s = h_encode(md5_str)
    x_t = str(v)
    common = {
        "s0": 5, "s1": "", "x0": "1", "x1": "3.2.0", "x2": "Windows",
        "x3": "xhs-pc-web", "x4": "2.3.1", "x5": a1, "x6": x_t, "x7": x_s,
        "x8": b1, "x9": mrc(x_t + x_s), "x10": 1,
    }
    x_s_common = b64_encode(encode_utf8(json.dumps(common, separators=(',', ':'))))
    return {"x-s": x_s, "x-t": x_t, "x-s-common": x_s_common}


# ===== Cookie 工具 =====

def load_cookies():
    with open(COOKIE_FILE) as f:
        cookies = json.load(f)
    cookie_dict = {c['name']: c['value'] for c in cookies}
    cookie_str = '; '.join(f"{c['name']}={c['value']}" for c in cookies)
    return cookie_dict, cookie_str


# ===== HTTP 工具 =====

def xhs_get(uri, params_str, host=CREATOR_HOST):
    cookie_dict, cookie_str = load_cookies()
    a1 = cookie_dict.get('a1', '')
    full_uri = f"{uri}?{params_str}" if params_str else uri
    signs = sign(full_uri, a1=a1)
    cmd = ['curl', '-s', '--max-time', '15',
        '-H', f'Cookie: {cookie_str}',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '-H', 'Referer: https://creator.xiaohongshu.com/publish/publish',
        '-H', f'x-s: {signs["x-s"]}', '-H', f'x-t: {signs["x-t"]}', '-H', f'x-s-common: {signs["x-s-common"]}',
        f'{host}{full_uri}'
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout)


def xhs_post(uri, data, host=HOST):
    cookie_dict, cookie_str = load_cookies()
    a1 = cookie_dict.get('a1', '')
    signs = sign(uri, data, a1=a1)
    body = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    cmd = ['curl', '-s', '--max-time', '20', '-X', 'POST',
        '-H', f'Cookie: {cookie_str}',
        '-H', 'Content-Type: application/json;charset=UTF-8',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        '-H', 'Referer: https://creator.xiaohongshu.com/',
        '-H', 'Origin: https://creator.xiaohongshu.com',
        '-H', 'Accept: application/json, text/plain, */*',
        '-H', f'x-s: {signs["x-s"]}', '-H', f'x-t: {signs["x-t"]}', '-H', f'x-s-common: {signs["x-s-common"]}',
        '-d', body, f'{host}{uri}'
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout)


# ===== 图片上传 =====

def upload_image(image_path):
    """上传图片，返回 file_id"""
    # Get upload permit
    permit_data = xhs_get(
        "/api/media/v1/upload/web/permit",
        "biz_name=spectrum&scene=image&file_count=1&version=1&source=web"
    )
    permit = permit_data['data']['uploadTempPermits'][0]
    file_id = permit['fileIds'][0]
    token = permit['token']

    # Determine content type
    ext = Path(image_path).suffix.lower()
    content_type = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png'

    # Upload file
    upload_url = f"https://ros-upload.xiaohongshu.com/{file_id}"
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
        '--max-time', '30', '-X', 'PUT',
        '-H', f'X-Cos-Security-Token: {token}',
        '-H', f'Content-Type: {content_type}',
        '--data-binary', f'@{image_path}',
        upload_url
    ], capture_output=True, text=True)

    if r.stdout.strip() != '200':
        raise Exception(f"Image upload failed: HTTP {r.stdout.strip()}")

    return file_id, content_type


# ===== 发帖 =====

def publish_note(title, desc, tags=None, image_paths=None, is_private=False):
    """
    发布小红书图文笔记
    :param title: 标题（≤20字）
    :param desc: 正文内容
    :param tags: 话题标签列表，如 ['小米汽车', 'YU7']
    :param image_paths: 图片路径列表（本地文件）
    :param is_private: 是否私密发布
    :return: (success, note_id, share_link)
    """
    if tags is None:
        tags = []

    # Upload images
    images = []
    if image_paths:
        for img_path in image_paths:
            print(f"  📤 上传图片: {img_path}")
            file_id, content_type = upload_image(img_path)
            mime = content_type
            images.append({
                "file_id": file_id,
                "metadata": {"source": -1},
                "stickers": {"version": 2, "floating": []},
                "extra_info_json": json.dumps({"mimeType": mime})
            })
            print(f"  ✅ 上传成功: {file_id[:40]}...")

    hash_tag = [{"name": t.strip('#'), "type": 1} for t in tags]
    business_binds = json.dumps({
        "version": 1, "noteId": 0, "noteOrderBind": {},
        "notePostTiming": {"postTime": None}, "noteCollectionBind": {"id": ""}
    }, separators=(',', ':'))

    data = {
        "common": {
            "type": "normal",
            "title": title,
            "note_id": "",
            "desc": desc,
            "source": '{"type":"web","ids":"","extraInfo":{"subType":"official"}}',
            "business_binds": business_binds,
            "ats": [],
            "hash_tag": hash_tag,
            "post_loc": {},
            "privacy_info": {"op_type": 1, "type": int(is_private)},
        },
        "image_info": {"images": images},
        "video_info": None,
    }

    resp = xhs_post("/web_api/sns/v2/note", data)
    if resp.get('success'):
        note_id = resp['data']['id']
        share_link = resp.get('share_link', f"https://www.xiaohongshu.com/discovery/item/{note_id}")
        return True, note_id, share_link
    else:
        return False, None, resp.get('msg', str(resp))


def check_auth():
    """验证 Cookie 是否有效"""
    try:
        resp = xhs_get("/api/galaxy/creator/note/user/posted", "page=1&pageSize=1")
        return resp.get('success', False)
    except:
        return False


# ===== CLI 入口 =====

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='小红书云端发帖工具 v2.0')
    parser.add_argument('--check', action='store_true', help='验证 Cookie 是否有效')
    parser.add_argument('--title', type=str, help='帖子标题（≤20字）')
    parser.add_argument('--content', type=str, help='帖子正文')
    parser.add_argument('--tags', type=str, help='话题标签，逗号分隔，如: 小米汽车,YU7')
    parser.add_argument('--images', type=str, help='图片路径，逗号分隔（本地文件）')
    parser.add_argument('--private', action='store_true', help='私密发布')
    args = parser.parse_args()

    if args.check:
        ok = check_auth()
        print("✅ Cookie 有效，认证成功" if ok else "❌ Cookie 无效或已过期")
        sys.exit(0 if ok else 1)

    if not args.title or not args.content:
        print("❌ 需要提供 --title 和 --content")
        sys.exit(1)

    tags = [t.strip() for t in (args.tags or '').split(',') if t.strip()]
    images = [p.strip() for p in (args.images or '').split(',') if p.strip()]

    print(f"📝 发布中...")
    print(f"   标题: {args.title}")
    print(f"   标签: {tags}")
    print(f"   图片: {images or '无'}")
    print(f"   可见: {'私密' if args.private else '公开'}")

    ok, note_id, result = publish_note(
        args.title, args.content, tags, images or None, args.private
    )

    if ok:
        print(f"\n🎉 发布成功！")
        print(f"   note_id: {note_id}")
        print(f"   链接: {result}")
    else:
        print(f"\n❌ 发布失败: {result}")
        sys.exit(1)
