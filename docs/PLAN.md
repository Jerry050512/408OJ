# 408OJ 设计文档

## 1. 项目定位

408OJ 是一个面向**计算机学科专业基础综合（408）备考**的本地化在线评测系统（Online Judge），专注数据结构算法设计题（历年真题第 41 题大题为主），以真实考试标准约束 C 语言编码，帮助考生形成"考场可直接默写"的肌肉记忆。

核心特色：

1. **真题题库**：收录 2012–2026 年全部 408 数据结构算法设计大题（第 41 题为主，含 2012-42、2016-43 等编程大题），改造为标准输入输出格式，可在线评测。
2. **408 合规检查（Source Policy）**：静态检查提交代码——头文件白名单、禁用函数黑名单、禁止文件/进程/系统调用。模拟考场"只允许基础库"的环境，支持 `standard` / `strict`（王道标准，仅 stdio/stdlib 等）两级。
3. **考点体系**：题目按章节（线性表/栈队列串/树/图/查找排序）与细分考点标注，算法大题考点标注重要度 ★1–5；配套基础算法例题/习题，把大题考点拆解为可独立训练的小题。
4. **题解页面**：每题配套题解（考点 → 思路 → 分步设计 → 参考代码 → 复杂度 → 考场提示）。
5. **学习仪表盘**：按章节统计通过情况、真题完成情况、评测记录。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 后端 | Python 3.11 + FastAPI + Uvicorn | 快速开发、自带类型与测试生态 |
| 页面 | Jinja2 服务端渲染 + 自研设计系统 CSS + 原生 JS | 离线可用、无构建步骤、统一设计 Token |
| 编辑器 | 自研轻量代码编辑器（textarea + C 语法高亮覆盖层 + 行号） | 离线可用，零依赖 |
| 存储 | SQLite（单文件） | 本地零配置 |
| 评测 | GCC（MinGW）编译 + subprocess 沙箱（超时/内存/退出码检测） | 真实 C 评测 |
| 测试 | pytest + httpx TestClient | 单元 + API + 评测集成测试 |
| 版本管理 | git：develop 分支开发，里程碑合入 main | — |

## 3. 架构

```
408OJ/
├── run.py                  # 启动入口: python run.py [--port 8408]
├── requirements.txt
├── docs/PLAN.md            # 本文档
├── oj/
│   ├── config.py           # 路径/常量/评测默认配置
│   ├── db.py               # SQLite 连接、schema、迁移、查询助手
│   ├── policy.py           # 408 UML? -> 源码合规静态检查（头文件白名单/禁用函数）
│   ├── judge.py            # 评测机: 编译->运行->比对-> verdict
│   ├── seed.py             # 题库构建: 由 content 生成 problems+testcases(用参考实现生成期望输出)
│   ├── content/
│   │   ├── real_2012_2016.py  # 真题: 2012-41/42, 2013-41, 2014-41, 2015-41, 2016-43
│   │   ├── real_2017_2021.py  # 真题: 2017-41 ... 2021-41
│   │   ├── real_2022_2026.py  # 真题: 2022-41 ... 2026-41
│   │   └── practice.py        # 考点拆解练习题
│   └── web/
│       ├── app.py          # FastAPI 应用: 页面路由 + /api/v1 JSON API
│       ├── templates/      # base, index, problems, problem, solution, submissions, submission, stats, error
│       └── static/css|js/  # 设计系统 design.css、应用 app.js、编辑器 editor.js
└── tests/
    ├── test_policy.py      # 合规检查单测
    ├── test_judge.py       # 评测机单测 (AC/WA/TLE/RE/CE)
    ├── test_content.py     # 题库完整性: 每题有测试/题解/样例一致; 参考解全部 AC
    ├── test_api.py         # API 与页面路由测试
    └── conftest.py         # 临时库 + TestClient fixtures
```

## 4. 数据模型

- `problems`: id, code(`real-2013-41` / `prac-list-01`), title, kind(exam/practice), year, exam_no, chapter, tags(JSON), difficulty 1-3, importance 1-5, statement_md, input_md, output_md, samples(JSON), policy(JSON), time_limit_ms, memory_limit_kb, solution_md, ref_solution_c
- `testcases`: id, problem_id, ord, input, expected, is_sample
- `submissions`: id, problem_id, code, verdict, passed, total, max_time_ms, max_mem_kb, compile_msg, results(JSON), created_at

## 5. 评测设计

Verdict: `AC / WA / TLE / RE / CE / SE`（按通过测试点比例给分）。
比对规则：忽略行尾空白与文末空行（标准 OJ 规则）。
运行限制：默认 1000ms / 64MB；psutil 轮询峰值 RSS（可选），一律设置超时。
禁止行为在编译前经 policy 静态检查拦截，违规定为 `CE(policy)` 并给出违规说明。

源代码合规规则：
- 白名单头文件（standard）: stdio.h stdlib.h string.h ctype.h math.h limits.h stddef.h stdbool.h float.h
- strict（王道标准）额外禁用 string.h / ctype.h / math.h（逐题可配置）
- 永远禁用：文件 I/O(fopen/freopen/fclose/remove/rename…)、进程与系统(system/exec*/fork/popen)、线程、网络、Windows API、`gets`、内联汇编、`#include` 绝对路径。

## 6. 页面与 API

页面：`/`(仪表盘) `/problems` `/p/{code}`(做题+提交+自测) `/p/{code}/solution` `/submissions` `/s/{id}` `/stats`
API：`GET /api/v1/problems` `GET /api/v1/problems/{code}` `POST /api/v1/submissions` `GET /api/v1/submissions/{id}` `GET /api/v1/stats` `POST /api/v1/run`（自定义输入试跑）

## 7. 题库规划

真题 16 道（全部重要度 ★5）：

| code | 题目 | 考点 |
|---|---|---|
| real-2012-41 | 多路升序表最小比较合并 | 哈夫曼思想/贪心 |
| real-2012-42 | 两单词链表公共后缀 | 单链表/对齐指针 |
| real-2013-41 | 数组主元素 | 计数/Boyer-Moore |
| real-2014-41 | 二叉树 WPL | RLR 遍历/递归 |
| real-2015-41 | 链表删绝对值重复结点 | 单链表/哈希计数 |
| real-2016-43 | 集合划分 | 排序/贪心 |
| real-2017-41 | 表达式树转中缀 | 二叉树递归/括号 |
| real-2018-41 | 未出现最小正整数 | 数组/原地哈希 |
| real-2019-41 | 链表重排 L1LnL2Ln-1… | 找中点+逆置+合并 |
| real-2020-41 | 三数组三元组最小距离 | 三指针 |
| real-2021-41 | EL 路径判定 | 邻接矩阵/度 |
| real-2022-41 | 顺序树判定 BST | 二叉搜索树/顺序存储 |
| real-2023-41 | 输出 K 顶点 | 邻接矩阵/出入度 |
| real-2024-41 | 唯一拓扑序列判定 | 拓扑排序 |
| real-2025-41 | 后缀乘积最大值 res[i] | 数组/一次遍历 |
| real-2026-41 | BST 最近关键字 | BST 查找/遍历 |

练习题 26 道（已实现），按大题考点拆解（链表逆置、找中点、快排划分、栈判定出栈序列、括号匹配、KMP next、先中序重建、树高/结点数、层序遍历、图的度、DFS/BFS、二分查找、堆插入、归并等），重要度 ★2–4 标注。选择题高频考点（如出栈序列、next 数组）一并收录。

## 8. 测试与验收

- `pytest` 全绿；参考解（C）对每题全部测试点 AC 作为强验收。
- 浏览器实际打开页面做冒烟测试。
- 里程碑提交：M1 核心评测 → M2 题库 → M3 Web/API → M4 打磨与文档 → 合并 main。

## 9. 里程碑完成情况

- [x] M1 核心：db / policy / judge + 29 项单测
- [x] M2 题库：42 题（16 真题 + 26 练习），参考解 C 全部 AC，完整性测试固化
- [x] M3 Web/API：设计系统（深/浅主题）、离线编辑器、全部页面 + API，51 项测试通过
- [x] M4 浏览器冒烟测试（首页/题库/做题/题解/提交记录/浅色主题）+ README

### 开发中发现并修复的关键问题

1. 评测机子进程 stdout 管道缓冲满导致假 TLE → 改为临时文件重定向输出。
2. 哈夫曼参考解 `sift_down` 多层下滤后基准值污染（经典堆 bug）→ 改为对暂存值比较，200 组随机数据与 heapq 对齐。
3. `from __future__ import annotations` 的字符串化注解使函数内 pydantic 模型无法解析（422）→ 模型移到模块级。
4. 真题转 OJ 格式时的格式归一化（2023-41 空输出行、2025-41 溢出、2019 链表归并边界）等由"样例 vs 参考实现"的 seed 期校验兜底。
