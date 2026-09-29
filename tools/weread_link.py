"""生成微信读书网页版的书籍/章节直达链接。

用法：python3 tools/weread_link.py <bookId> [chapterUid ...]
bookId、chapterUid 可在微信读书网页版的接口数据中找到。
"""
import hashlib
import sys


def encode(value: str) -> str:
    digest = hashlib.md5(value.encode()).hexdigest()
    out = digest[:3] + "32" + digest[-2:]
    parts = [format(int(value[i:i + 9]), "x") for i in range(0, len(value), 9)]
    out += "g".join(format(len(p), "02x") + p for p in parts)
    if len(out) < 20:
        out += digest[:20 - len(out)]
    return out + hashlib.md5(out.encode()).hexdigest()[:3]


if __name__ == "__main__":
    book, *chapters = sys.argv[1:]
    base = "https://weread.qq.com/web/reader/" + encode(book)
    print(base)
    for uid in chapters:
        print(uid, base + "k" + encode(uid))
