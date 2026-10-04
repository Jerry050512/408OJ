#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""408OJ 本地启动入口。

用法：
    python run.py [--host 127.0.0.1] [--port 8408] [--db PATH] [--reseed]
"""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="408OJ local judge server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8408)
    parser.add_argument("--db", default=None, help="SQLite 数据文件路径")
    parser.add_argument("--reseed", action="store_true", help="重建题库（ submissions 保留）")
    args = parser.parse_args()

    from pathlib import Path
    from oj import config, db as dbm, seed

    db_path = Path(args.db) if args.db else config.DB_PATH
    config.BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if args.reseed:
        conn = dbm.connect(db_path)
        n = seed.seed_database(conn)
        conn.close()
        print(f"[seed] {n} problems rebuilt")

    import uvicorn
    from oj.web.app import create_app

    app = create_app(db_path)
    print(f"408OJ running at http://{args.host}:{args.port}  (db: {db_path})")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    sys.exit(main())
