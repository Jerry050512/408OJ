# -*- coding: utf-8 -*-
"""模拟题生成器与参考实现。函数命名：gen_{code} / ref_{code}（code 中 - 替换为 _）。"""
from __future__ import annotations

import random


def ints_line(arr):
    return " ".join(str(x) for x in arr) + "\n"


# ── mock-01 链表分组逆置 ──────────────────────────────────────
def gen_mock_01(seed):
    rng = random.Random(seed)
    cases = []
    for n in (5, 8, 12, 20):
        k = rng.randint(2, n)
        arr = [rng.randint(1, 99) for _ in range(n)]
        cases.append(f"{n} {k}\n{ints_line(arr)}")
    n = 30; k = rng.randint(2, n)
    arr = [rng.randint(1, 99) for _ in range(n)]
    cases.append(f"{n} {k}\n{ints_line(arr)}")
    return cases


def ref_mock_01(case):
    t = case.split()
    n, k = int(t[0]), int(t[1])
    arr = [int(x) for x in t[2:2 + n]]
    out = []
    for i in range(0, n, k):
        g = arr[i:i + k]
        out.extend(reversed(g) if len(g) == k else g)
    return ints_line(out)


# ── mock-02 数组循环右移k位 ────────────────────────────────────
def gen_mock_02(seed):
    rng = random.Random(seed)
    cases = []
    for n in (5, 8, 10, 15):
        k = rng.randint(0, n - 1)
        arr = [rng.randint(1, 99) for _ in range(n)]
        cases.append(f"{n} {k}\n{ints_line(arr)}")
    n = 25; k = rng.randint(0, n - 1)
    arr = [rng.randint(1, 99) for _ in range(n)]
    cases.append(f"{n} {k}\n{ints_line(arr)}")
    return cases


def ref_mock_02(case):
    t = case.split()
    n, k = int(t[0]), int(t[1])
    arr = [int(x) for x in t[2:2 + n]]
    k = k % n if n else 0
    return ints_line(arr[n - k:] + arr[:n - k])


# ── mock-03 两个升序数组的中位数 ───────────────────────────────
def gen_mock_03(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n, m = rng.randint(1, 10), rng.randint(1, 10)
        a = sorted(rng.sample(range(1, 100), n))
        b = sorted(rng.sample(range(1, 100), m))
        cases.append(f"{n} {m}\n{ints_line(a)}{ints_line(b)}")
    return cases


def ref_mock_03(case):
    lines = case.strip().split("\n")
    n, m = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    b = list(map(int, lines[2].split()))
    merged = sorted(a + b)
    return f"{merged[(n + m - 1) // 2]}\n"


# ── mock-04 链表删除所有值为x的结点 ───────────────────────────
def gen_mock_04(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 20)
        arr = [rng.randint(1, 10) for _ in range(n)]
        x = rng.choice(arr)
        cases.append(f"{n} {x}\n{ints_line(arr)}")
    return cases


def ref_mock_04(case):
    t = case.split()
    n, x = int(t[0]), int(t[1])
    arr = [int(v) for v in t[2:2 + n]]
    out = [v for v in arr if v != x]
    return ints_line(out) if out else "\n"


# ── mock-05 数组中超过⌊n/k⌋的众数 ────────────────────────────
def gen_mock_05(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 30)
        k = rng.randint(2, 5)
        arr = [rng.randint(1, 10) for _ in range(n)]
        cases.append(f"{n} {k}\n{ints_line(arr)}")
    return cases


def ref_mock_05(case):
    t = case.split()
    n, k = int(t[0]), int(t[1])
    arr = [int(x) for x in t[2:2 + n]]
    from collections import Counter
    cnt = Counter(arr)
    threshold = n // k
    result = sorted(v for v, c in cnt.items() if c > threshold)
    return ints_line(result) if result else "\n"


# ── mock-06 有序数组去重 ──────────────────────────────────────
def gen_mock_06(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 30)
        arr = sorted(rng.randint(1, 15) for _ in range(n))
        cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_mock_06(case):
    t = case.split()
    n = int(t[0])
    arr = [int(x) for x in t[1:1 + n]]
    out = []
    for v in arr:
        if not out or out[-1] != v:
            out.append(v)
    return ints_line(out)


# ── mock-07 数组最长连续递增子序列 ────────────────────────────
def gen_mock_07(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 30)
        arr = [rng.randint(1, 50) for _ in range(n)]
        cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_mock_07(case):
    t = case.split()
    n = int(t[0])
    arr = [int(x) for x in t[1:1 + n]]
    if n == 0:
        return "0\n"
    best = cur = 1
    for i in range(1, n):
        if arr[i] > arr[i - 1]:
            cur += 1
        else:
            cur = 1
        if cur > best:
            best = cur
    return f"{best}\n"


# ── mock-08 BST中第k小元素 ────────────────────────────────────
def gen_mock_08(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 20)
        vals = rng.sample(range(1, 100), n)
        k = rng.randint(1, n)
        cases.append(f"{n} {k}\n{ints_line(vals)}")
    return cases


def ref_mock_08(case):
    t = case.split()
    n, k = int(t[0]), int(t[1])
    vals = [int(x) for x in t[2:2 + n]]
    return f"{sorted(vals)[k - 1]}\n"


# ── mock-09 判断二叉树是否对称 ────────────────────────────────
def gen_mock_09(seed):
    rng = random.Random(seed)
    cases = []
    # symmetric trees
    for n in (1, 3, 7, 15):
        arr = ["-1"] * n
        arr[0] = str(rng.randint(1, 9))
        queue = [0]
        for i in queue:
            l, r = 2 * i + 1, 2 * i + 2
            if l >= n:
                continue
            v = rng.randint(1, 9)
            arr[l] = str(v)
            if r < n:
                arr[r] = str(v)
                queue.append(l); queue.append(r)
        cases.append(f"{n}\n{' '.join(arr)}\n")
    # non-symmetric
    cases.append("5\n1 2 3 -1 4\n")
    cases.append("3\n1 2 -1\n")
    return cases


def ref_mock_09(case):
    t = case.split()
    n = int(t[0])
    a = t[1:1 + n]

    def sym(i, j):
        if i >= n and j >= n:
            return True
        if i >= n or j >= n:
            return False
        if a[i] == "-1" and a[j] == "-1":
            return True
        if a[i] == "-1" or a[j] == "-1":
            return False
        if a[i] != a[j]:
            return False
        return sym(2 * i + 1, 2 * j + 2) and sym(2 * i + 2, 2 * j + 1)

    if n == 0 or a[0] == "-1":
        return "1\n"
    return ("1" if sym(1, 2) else "0") + "\n"


# ── mock-10 二叉树叶子结点数 ──────────────────────────────────
def gen_mock_10(seed):
    rng = random.Random(seed)
    cases = []
    for n in (1, 3, 7, 15):
        arr = ["-1"] * n
        arr[0] = str(rng.randint(1, 9))
        queue = [0]
        for i in queue:
            if 2 * i + 1 >= n:
                continue
            for c in (2 * i + 1, 2 * i + 2):
                if rng.random() < 0.8:
                    arr[c] = str(rng.randint(1, 9))
                    queue.append(c)
        cases.append(f"{n}\n{' '.join(arr)}\n")
    return cases


def ref_mock_10(case):
    t = case.split()
    n = int(t[0])
    a = t[1:1 + n]

    def count(i):
        if i >= n or a[i] == "-1":
            return 0
        l, r = 2 * i + 1, 2 * i + 2
        has_l = l < n and a[l] != "-1"
        has_r = r < n and a[r] != "-1"
        if not has_l and not has_r:
            return 1
        return count(l) + count(r)

    return f"{count(0)}\n"


# ── mock-11 二叉树的最大路径和 ────────────────────────────────
def gen_mock_11(seed):
    rng = random.Random(seed)
    cases = []
    for n in (1, 3, 7, 15):
        arr = ["-1"] * n
        arr[0] = str(rng.randint(-5, 10))
        queue = [0]
        for i in queue:
            if 2 * i + 1 >= n:
                continue
            for c in (2 * i + 1, 2 * i + 2):
                if rng.random() < 0.75:
                    arr[c] = str(rng.randint(-5, 10))
                    queue.append(c)
        cases.append(f"{n}\n{' '.join(arr)}\n")
    return cases


def ref_mock_11(case):
    t = case.split()
    n = int(t[0])
    a = [int(x) for x in t[1:1 + n]]
    best = [a[0] if n > 0 and a[0] != -1 else 0]

    def dfs(i):
        if i >= n or a[i] == -1:
            return 0
        left = max(0, dfs(2 * i + 1))
        right = max(0, dfs(2 * i + 2))
        best[0] = max(best[0], a[i] + left + right)
        return a[i] + max(left, right)

    if n == 0 or a[0] == -1:
        return "0\n"
    dfs(0)
    return f"{best[0]}\n"


# ── mock-12 BST删除关键字 ─────────────────────────────────────
def gen_mock_12(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(2, 15)
        vals = rng.sample(range(1, 50), n)
        x = rng.choice(vals)
        cases.append(f"{n} {x}\n{ints_line(vals)}")
    return cases


def ref_mock_12(case):
    t = case.split()
    n, x = int(t[0]), int(t[1])
    vals = [int(v) for v in t[2:2 + n]]

    class Node:
        def __init__(self, v):
            self.v = v; self.l = self.r = None

    def insert(t, v):
        if not t: return Node(v)
        if v < t.v: t.l = insert(t.l, v)
        elif v > t.v: t.r = insert(t.r, v)
        return t

    def delete(t, v):
        if not t: return None
        if v < t.v: t.l = delete(t.l, v)
        elif v > t.v: t.r = delete(t.r, v)
        else:
            if not t.l: return t.r
            if not t.r: return t.l
            cur = t.r
            while cur.l: cur = cur.l
            t.v = cur.v
            t.r = delete(t.r, cur.v)
        return t

    def inorder(t):
        if not t: return []
        return inorder(t.l) + [t.v] + inorder(t.r)

    root = None
    for v in vals:
        root = insert(root, v)
    root = delete(root, x)
    out = inorder(root)
    return ints_line(out) if out else "\n"


# ── mock-13 有向图欧拉回路判定 ────────────────────────────────
def gen_mock_13(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 10)
        m = rng.randint(0, min(n * (n - 1), 20))
        edges = set()
        while len(edges) < m:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                edges.add((u, v))
        edges = sorted(edges)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_mock_13(case):
    toks = case.split()
    p = 0
    n, m = int(toks[p]), int(toks[p + 1]); p += 2
    indeg = [0] * n
    outdeg = [0] * n
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        outdeg[u] += 1; indeg[v] += 1
        adj[u].append(v); radj[v].append(u)
    # 条件1: indeg == outdeg for all
    if any(indeg[i] != outdeg[i] for i in range(n)):
        return "0\n"
    # 条件2: all vertices with nonzero degree are weakly connected
    # Use undirected BFS on adj+radj
    has_edge = [i for i in range(n) if indeg[i] + outdeg[i] > 0]
    if not has_edge:
        return "1\n"
    vis = [False] * n
    q = [has_edge[0]]
    vis[has_edge[0]] = True
    while q:
        u = q.pop()
        for w in adj[u] + radj[u]:
            if not vis[w]:
                vis[w] = True; q.append(w)
    if all(vis[i] for i in has_edge):
        return "1\n"
    return "0\n"


# ── mock-14 无向图判断是否为树 ────────────────────────────────
def gen_mock_14(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 10)
        m = rng.randint(0, min(n * (n - 1) // 2, 20))
        edges = set()
        while len(edges) < m:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        edges = sorted(edges)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_mock_14(case):
    toks = case.split()
    p = 0
    n, m = int(toks[p]), int(toks[p + 1]); p += 2
    if m != n - 1:
        return "0\n"
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        parent[find(u)] = find(v)
    roots = {find(i) for i in range(n)}
    return ("1" if len(roots) == 1 else "0") + "\n"


# ── mock-15 有向图环检测 ──────────────────────────────────────
def gen_mock_15(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 10)
        perm = list(range(n)); rng.shuffle(perm)
        pos = {v: i for i, v in enumerate(perm)}
        edges = set()
        for _ in range(rng.randint(0, min(n * (n - 1) // 2, 15))):
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v and pos[u] < pos[v]:
                edges.add((u, v))
        # sometimes add a back edge to create cycle
        if rng.random() < 0.4 and n >= 2:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v and pos[u] > pos[v]:
                edges.add((u, v))
        edges = sorted(edges)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_mock_15(case):
    toks = case.split()
    p = 0
    n, m = int(toks[p]), int(toks[p + 1]); p += 2
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        adj[u].append(v); indeg[v] += 1
    q = [i for i in range(n) if indeg[i] == 0]
    cnt = 0
    while q:
        u = q.pop(); cnt += 1
        for w in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    return ("0" if cnt == n else "1") + "\n"


# ── mock-16 无向图的割点 ──────────────────────────────────────
def gen_mock_16(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(2, 8)
        m = rng.randint(0, min(n * (n - 1) // 2, 12))
        edges = set()
        while len(edges) < m:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        edges = sorted(edges)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_mock_16(case):
    toks = case.split()
    p = 0
    n, m = int(toks[p]), int(toks[p + 1]); p += 2
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        adj[u].append(v); adj[v].append(u)
    # Brute force: for each vertex v, check if removing v increases components
    def components_without(exclude):
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for u in range(n):
            if u == exclude:
                continue
            for w in adj[u]:
                if w == exclude:
                    continue
                parent[find(u)] = find(w)
        return len({find(i) for i in range(n) if i != exclude})

    base = components_without(-1)  # all vertices
    cuts = []
    for v in range(n):
        if components_without(v) > base:
            cuts.append(v)
    return f"{len(cuts)}\n{' '.join(map(str, cuts))}\n" if cuts else "0\n\n"


# ── mock-17 堆中第k大元素 ─────────────────────────────────────
def gen_mock_17(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 30)
        k = rng.randint(1, n)
        arr = [rng.randint(1, 100) for _ in range(n)]
        cases.append(f"{n} {k}\n{ints_line(arr)}")
    return cases


def ref_mock_17(case):
    t = case.split()
    n, k = int(t[0]), int(t[1])
    arr = [int(x) for x in t[2:2 + n]]
    import heapq
    return f"{heapq.nlargest(k, arr)[-1]}\n"


# ── mock-18 散列表构建与查找 ──────────────────────────────────
def gen_mock_18(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        m = rng.choice([7, 11, 13, 17, 19])
        n = rng.randint(1, m)
        q = rng.randint(1, 8)
        keys = rng.sample(range(1, 100), n)
        queries = [rng.randint(1, 100) for _ in range(q)]
        cases.append(f"{m} {n} {q}\n{ints_line(keys)}{ints_line(queries)}")
    return cases


def ref_mock_18(case):
    lines = case.strip().split("\n")
    m, n, q = map(int, lines[0].split())
    keys = list(map(int, lines[1].split()))
    queries = list(map(int, lines[2].split()))
    table = [None] * m
    for k in keys:
        h = k % m
        while table[h] is not None:
            h = (h + 1) % m
        table[h] = k
    out = []
    for k in queries:
        h = k % m
        found = False
        for _ in range(m):
            if table[h] is None:
                break
            if table[h] == k:
                out.append(str(h)); found = True; break
            h = (h + 1) % m
        if not found:
            out.append("-1")
    return " ".join(out) + "\n"
