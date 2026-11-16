# -*- coding: utf-8 -*-
"""把 build/geo.json、build/data.json 和每个单位的颜色注入 src/template.html，生成不依赖外部文件的 docs/index.html。
英文与中文写在同一处（content/ 各文件），不另设译文表。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402


def main():
    tpl = C.TEMPLATE.read_text(encoding="utf8")
    geo = json.loads((C.BUILD / "geo.json").read_text(encoding="utf8"))
    data = json.loads((C.BUILD / "data.json").read_text(encoding="utf8"))
    colors = json.loads((C.BUILD / "colors.json").read_text(encoding="utf8"))
    light = " ".join(f"--u-{i}:{c};" for i, c in enumerate(colors["light"]))
    dark = " ".join(f"--u-{i}:{c};" for i, c in enumerate(colors["dark"]))
    for k in ("__GEO__", "__DATA__", "__UCSS_LIGHT__", "__UCSS_DARK__"):
        assert k in tpl, f"模板缺少占位符 {k}"
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = (tpl.replace("__UCSS_LIGHT__", light).replace("__UCSS_DARK__", dark)
               .replace("__DATA__", dump(data)).replace("__GEO__", dump(geo)))
    C.DOCS.mkdir(exist_ok=True)
    C.OUT_HTML.write_text(html, encoding="utf8")
    print(f"   {C.OUT_HTML.relative_to(C.ROOT)}  {len(html.encode('utf8')) // 1024} KB")


if __name__ == "__main__":
    main()
