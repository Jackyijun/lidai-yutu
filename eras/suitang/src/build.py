# 底图与汇编，输出 build/*.json：底图 geo_base.json → 汇编 out_data.json（再由 src/assemble.py 写成本卷的 source.json）
# 疆域不在这里算：由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json）。
# 本卷原来的势力格（src/territory.py）2026-11 架构整理第三批起退役。
import sys, time
import config as C

sys.path[:0] = [str(C.CONTENT)]


def main(full=True):
    """full = False（python run.py --html）时已有 build/geo_base.json 就不重做底图"""
    t0 = time.time()
    C.BUILD.mkdir(exist_ok=True)
    import fetch_data
    fetch_data.main()
    if full or not (C.BUILD / 'geo_base.json').exists():
        import basemap
        basemap.main()
    import compile_data
    compile_data.main()
    print(f'  [构建] {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
