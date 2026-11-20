# -*- coding: utf-8 -*-
"""秦郡：统一引擎（era.toml [engine] sub）把秦的疆域按郡治就近再分一层，页面画成秦郡界（节点 ext j）。

  UNIT    被细分的单位
  HOSTS   郡治须落在这些单位的疆域里才参与（东郡治濮阳，前241 起卫君徙野王，濮阳一带仍按旧构建计入）
  NEAR    离 HOSTS 疆域不到这么多格（约 7 公里一格）的郡治也算：郡治在两方交界、新旧分区稍有出入时不致整郡消失
          （洞庭郡治取常德一带，在秦的黔中与楚的临沅之间，新引擎分给了临沅）
  seats() [(郡键, 经, 纬, 始置年)]，取 content/features.py 的 JUN；郡键与页面条目一致（如「四川」「临菑」）

同旧构建（src/build.py「秦郡」一节）：已始置、治所在秦或卫境内的郡，在秦的格子里按代价就近分区。
"""
import importlib.util
from pathlib import Path

UNIT = "秦"
HOSTS = ("秦", "卫")
NEAR = 4


def seats():
    p = Path(__file__).resolve().parents[1] / "content" / "features.py"
    spec = importlib.util.spec_from_file_location("zhanguo_features_jun", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return [(j[0], j[3], j[4], j[5]) for j in m.JUN]
