# -*- coding: utf-8 -*-
"""408 真题 2022–2026（第 41 题算法设计）。"""
from __future__ import annotations

import random


def ints_line(arr):
    return " ".join(str(x) for x in arr) + "\n"


# ============================================================
# 2022-41 顺序存储二叉树的 BST 判定
# ============================================================
def gen_2022_41(seed):
    rng = random.Random(seed)
    cases = []

    def rand_tree_arr(size, as_bst):
        arr = [-1] * size

        def fill(i, lo, hi):
            if i >= size or rng.random() < 0.25:
                return
            if as_bst:
                v = rng.randint(lo + 1, hi - 1) if hi - lo > 1 else lo
            else:
                v = rng.randint(1, 99)
            arr[i] = v
            fill(2 * i + 1, lo, v)
            fill(2 * i + 2, v, hi)

        arr2 = list(arr)
        fill(0, 0, 100)
        return arr

    for _ in range(4):
        size = rng.randint(1, 31)
        arr = rand_tree_arr(size, True)
        cases.append(f"{size}\n{ints_line(arr)}")
    for _ in range(4):
        size = rng.randint(1, 31)
        arr = rand_tree_arr(size, False)
        arr[0] = rng.randint(40, 60) if arr[0] == -1 else arr[0]
        cases.append(f"{size}\n{ints_line(arr)}")
    cases.append("10\n40 25 60 -1 30 -1 80 -1 -1 27\n")   # 真题 T1 -> 1
    cases.append("11\n40 50 60 -1 30 -1 -1 -1 -1 -1 35\n") # 真题 T2 -> 0
    return cases


def ref_2022_41(case):
    toks = case.split()
    n = int(toks[0])
    a = [int(x) for x in toks[1:1 + n]]

    def check(i, lo, hi):
        """结点值 v 必须满足 lo < v < hi"""
        if i >= n or a[i] == -1:
            return True
        v = a[i]
        if not (lo < v < hi):
            return False
        return check(2 * i + 1, lo, v) and check(2 * i + 2, v, hi)

    if n == 0:
        return "1\n"
    return ("1" if check(0, float("-inf"), float("inf")) else "0") + "\n"


S_2022_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

int n;
long *a; /* -1 为空；用 long 以便上下界取极值 */

/* 递归判定：结点 i 的值必须落在 (lo, hi) 开区间内 */
static int check(int i, long lo, long hi){
    if (i >= n || a[i] == -1) return 1;
    if (a[i] <= lo || a[i] >= hi) return 0;
    return check(2*i + 1, lo, a[i]) && check(2*i + 2, a[i], hi);
}

int main(void){
    if (scanf("%d", &n) != 1) return 0;
    a = (long*)malloc(sizeof(long) * (n > 0 ? n : 1));
    for (int i = 0; i < n; i++) scanf("%ld", &a[i]);
    /* 初始区间 (-inf, +inf)，用足够大的哨兵 */
    printf("%d\n", check(0, -1000000001L, 1000000001L));
    free(a);
    return 0;
}
"""

S_2022_41_SOLUTION = """## 考点

二叉搜索树（BST）+ 顺序存储（王道 5.1/5.4）。2022 年的新意只在于存储方式，算法本身仍是经典 BST 判定。

## 思路

BST 的核心约束不是"左孩子 < 根 < 右孩子"，而是**每个结点落在祖先界定的开区间 (lo, hi) 内**：

- 根结点：(-∞, +∞)；
- 左孩子 i → (lo, v)，右孩子 i → (v, hi)；
- 遇到 -1 即空，直接合法。

顺序存储中，结点 i 的左右孩子下标为 2i+1 / 2i+2（注意真题 SqBiTree 不清空越界部分，判断 `i >= ElemNum` 即视为空）。

等价写法：**中序遍历应严格递增**。递归区间法直观好写，考场推荐。

## 复杂度

时间 O(n)，空间 O(h)。

## 考场提示

- 区间端点是**开区间**（BST 不允许重复关键字）；
- 用 int 比较时留意题目值域，选用 long 或足够大的哨兵更稳；
- 根不存在（ElemNum=0 / 首元素 -1）时按 BST 处理还是非法，以题目"非空"设定为准。
"""

P_2022_41 = dict(
    code="real-2022-41", title="顺序存储二叉树的 BST 判定", kind="exam", year=2022,
    exam_no="第41题", chapter="树与二叉树", tags=["二叉搜索树", "顺序存储", "递归"],
    difficulty=3, importance=5,
    statement_md=(
        "已知非空二叉树 T 的结点值均为正整数，采用**顺序存储**方式保存："
        "数组下标 i 的结点，其左右孩子下标为 2i+1、2i+2；不存在的结点在数组中用 **−1** 表示。\n\n"
        "请设计一个尽可能高效的算法，判定 T 是否为**二叉搜索树**，若是输出 1，否则输出 0。"
    ),
    input_md=(
        "第一行一个整数 n（1 ≤ n ≤ 10⁵），表示存储数组长度。\n"
        "第二行 n 个整数（−1 表示空结点，其余为正整数）。"),
    output_md="输出 1（是 BST）或 0（不是）。",
    samples=[{"input": "10\n40 25 60 -1 30 -1 80 -1 -1 27\n", "output": "1\n"},
             {"input": "11\n40 50 60 -1 30 -1 -1 -1 -1 -1 35\n", "output": "0\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 顺序存储：i 的孩子 2i+1 / 2i+2，-1 为空 */\n"
        "int check(int i, long lo, long hi);\n\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n    return 0;\n}\n"),
    ref_c=S_2022_41_REF_C,
    gen=gen_2022_41, ref_py=ref_2022_41,
    solution_md=S_2022_41_SOLUTION,
)

# ============================================================
# 2023-41 K 顶点（出度 > 入度）
# ============================================================
def gen_2023_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 12)
        m = rng.randint(0, min(n * (n - 1), 30))
        edges = set()
        while len(edges) < m:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                edges.add((u, v))
        edges = sorted(edges)
        out = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(out) + "\n")
    return cases


def ref_2023_41(case):
    toks = case.split()
    p = 0
    n = int(toks[p]); m = int(toks[p + 1]); p += 2
    indeg = [0] * n
    outdeg = [0] * n
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        outdeg[u] += 1
        indeg[v] += 1
    ks = [i for i in range(n) if outdeg[i] > indeg[i]]
    return f"{len(ks)}\n{' '.join(map(str, ks))}\n"


S_2023_41_REF_C = r"""
#include <stdio.h>

#define MAXV 105

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    static int edge[MAXV][MAXV];
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        edge[u][v] = 1;
    }
    /* 第 i 行和为出度，第 i 列和为入度 */
    int cnt = 0;
    static int ks[MAXV];
    for (int i = 0; i < n; i++){
        int od = 0, idg = 0;
        for (int j = 0; j < n; j++){ od += edge[i][j]; idg += edge[j][i]; }
        if (od > idg) ks[cnt++] = i;
    }
    printf("%d\n", cnt);
    for (int i = 0; i < cnt; i++){
        if (i) putchar(' ');
        printf("%d", ks[i]);
    }
    putchar('\n');
    return 0;
}
"""

S_2023_41_SOLUTION = """## 考点

图的邻接矩阵遍历（王道 6.1）。行扫描 = 出度，列扫描 = 入度，这是邻接矩阵题的基本功。

## 思路

对每个顶点 i：

- 出度 = 邻接矩阵第 i 行元素之和；
- 入度 = 第 i 列元素之和；
- 出度 > 入度即为 K 顶点，输出并计数。

## 复杂度

时间 O(n²)，空间 O(1)（不计输出数组）。真题同时考"面向对象/行优先高速缓存"，回答按行扫描的局部性更优可以加分。

## 考场提示

- 顶点编号从 0 开始；按编号升序输出；
- count 单独输出一行，顶点序列再输出一行，方便机器评测；
- 重边按矩阵元素累加（本题为 0/1 矩阵）。
"""

P_2023_41 = dict(
    code="real-2023-41", title="有向图的 K 顶点输出", kind="exam", year=2023,
    exam_no="第41题", chapter="图", tags=["邻接矩阵", "出入度"],
    difficulty=1, importance=5,
    statement_md=(
        "已知有向图 G 采用邻接矩阵存储。将图中**出度大于入度**的顶点称为 K 顶点。\n\n"
        "设计算法输出 G 中所有 K 顶点（按编号升序），并在第一行输出 K 顶点的个数。"
    ),
    input_md=(
        "第一行两个整数 n（顶点数，编号 0..n-1）和 m（边数）。\n"
        "之后 m 行，每行两个整数 u v，表示有向边 u → v。"),
    output_md=(
        "第一行输出 K 顶点的个数 k。\n"
        "第二行按升序输出 k 个 K 顶点的编号，空格分隔（k 为 0 时第二行为空）。"),
    samples=[{"input": "4 5\n0 1\n0 2\n1 2\n1 3\n3 0\n", "output": "2\n0 1\n"},
             {"input": "3 0\n", "output": "0\n\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n\n#define MAXV 105\n\n"
        "int main(void){\n    int n, m;\n    scanf(\"%d %d\", &n, &m);\n"
        "    /* TODO: 建邻接矩阵，行列扫描求出入度 */\n    return 0;\n}\n"),
    ref_c=S_2023_41_REF_C,
    gen=gen_2023_41, ref_py=ref_2023_41,
    solution_md=S_2023_41_SOLUTION,
)

# ============================================================
# 2024-41 唯一拓扑序列判定
# ============================================================
def gen_2024_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 10)
        # 随机 DAG：按随机全序加边
        perm = list(range(n))
        rng.shuffle(perm)
        pos = {v: i for i, v in enumerate(perm)}
        edges = set()
        for _ in range(rng.randint(0, min(n * (n - 1) // 2, 20))):
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v and pos[u] < pos[v]:
                edges.add((u, v))
        edges = sorted(edges)
        out = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(out) + "\n")
    return cases


def ref_2024_41(case):
    toks = case.split()
    p = 0
    n = int(toks[p]); m = int(toks[p + 1]); p += 2
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        adj[u].append(v)
        indeg[v] += 1
    queue = [i for i in range(n) if indeg[i] == 0]
    cnt = 0
    unique = True
    while queue:
        if len(queue) > 1:
            unique = False
        # 任取一个（判定唯一性时取谁都等价）
        u = queue.pop()
        cnt += 1
        for w in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)
    return ("1" if (unique and cnt == n) else "0") + "\n"


S_2024_41_REF_C = r"""
#include <stdio.h>

#define MAXV 1005

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    static int adj[MAXV][MAXV];
    int indeg[MAXV] = {0};
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        if (!adj[u][v]){ adj[u][v] = 1; indeg[v]++; }
    }
    /* 拓扑排序：若任一时刻入度为 0 的顶点不止一个，则拓扑序列不唯一 */
    int queue[MAXV], head = 0, tail = 0;
    for (int i = 0; i < n; i++) if (indeg[i] == 0) queue[tail++] = i;
    int cnt = 0, unique = 1;
    while (head < tail){
        if (tail - head > 1) unique = 0;
        int u = queue[head++];
        cnt++;
        for (int v = 0; v < n; v++){
            if (adj[u][v] && --indeg[v] == 0) queue[tail++] = v;
        }
    }
    /* cnt < n 说明有环，同样输出 0 */
    printf("%d\n", (unique && cnt == n) ? 1 : 0);
    return 0;
}
"""

S_2024_41_SOLUTION = """## 考点

拓扑排序（王道 6.4）。2024 年新题核心结论：**拓扑序列唯一 ⟺ 每一轮"可输出"（入度为 0）的顶点都只有一个**。

## 思路

按 Kahn 算法做拓扑排序，每轮统计队列中入度为 0 的顶点数：

- 一旦 > 1：这一步任选都能产生合法序列，故不唯一 → 输出 0；
- 全部恰好 1 且最终输出顶点数 == n（无环）→ 唯一 → 输出 1；
- 有环（cnt < n）也不存在拓扑序列 → 0。

## 复杂度

邻接矩阵时间 O(n²)，邻接表 O(n+m)；空间 O(n)。

## 考场提示

- 记好 Kahn 模板：入度数组 + 队列；每删一个点把其后继入度减一；
- "存在" 与 "唯一" 只差一句 `queue size > 1` 的判定；
- 有向无环图也不一定有唯一拓扑序列（如两条平行边结构的两个源点）。
"""

P_2024_41 = dict(
    code="real-2024-41", title="唯一拓扑序列判定", kind="exam", year=2024,
    exam_no="第41题", chapter="图", tags=["拓扑排序", "邻接矩阵"],
    difficulty=2, importance=5,
    statement_md=(
        "载人航天工程包含众多子工程，为保证工程有序开展，需要明确各子工程的前导工程。"
        "该问题可抽象为有向图的拓扑序列问题。\n\n"
        "请设计算法判定有向图 G 是否存在**唯一的拓扑序列**：存在唯一拓扑序列输出 1，"
        "否则输出 0（图中有环时也输出 0）。"
    ),
    input_md=(
        "第一行两个整数 n（顶点数，编号 0..n-1）和 m（边数）。\n"
        "之后 m 行，每行两个整数 u v，表示有向边 u → v（不存在重复边）。"),
    output_md="输出 1 或 0。",
    samples=[{"input": "3 2\n0 1\n1 2\n", "output": "1\n"},
             {"input": "3 2\n0 2\n1 2\n", "output": "0\n"},
             {"input": "2 2\n0 1\n1 0\n", "output": "0\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n\n#define MAXV 1005\n\n"
        "int main(void){\n    int n, m;\n    scanf(\"%d %d\", &n, &m);\n"
        "    /* TODO: Kahn 拓扑排序，监测队列大小 */\n    return 0;\n}\n"),
    ref_c=S_2024_41_REF_C,
    gen=gen_2024_41, ref_py=ref_2024_41,
    solution_md=S_2024_41_SOLUTION,
)

# ============================================================
# 2025-41 res[i] = max A[i]*A[j] (j >= i)
# ============================================================
def gen_2025_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 30)
        arr = [rng.randint(-50, 50) for _ in range(n)]
        cases.append(f"{n}\n{ints_line(arr)}")
    n = 100000
    arr = [rng.randint(-10**6, 10**6) for _ in range(n)]
    cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_2025_41(case):
    toks = case.split()
    n = int(toks[0])
    a = [int(x) for x in toks[1:1 + n]]
    res = [0] * n
    mx = a[-1]
    mn = a[-1]
    for i in range(n - 1, -1, -1):
        if a[i] > mx:
            mx = a[i]
        if a[i] < mn:
            mn = a[i]
        res[i] = a[i] * mx if a[i] >= 0 else a[i] * mn
    return ints_line(res)


S_2025_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    long long *a = (long long*)malloc(sizeof(long long) * (n > 0 ? n : 1));
    long long *res = (long long*)malloc(sizeof(long long) * (n > 0 ? n : 1));
    for (int i = 0; i < n; i++) scanf("%lld", &a[i]);
    /* 自右向左维护后缀最大值/最小值 */
    long long mx = a[n - 1], mn = a[n - 1];
    for (int i = n - 1; i >= 0; i--){
        if (a[i] > mx) mx = a[i];
        if (a[i] < mn) mn = a[i];
        /* A[i]>=0 取后缀最大；否则取后缀最小（负数乘最小得最大） */
        res[i] = (a[i] >= 0) ? a[i] * mx : a[i] * mn;
    }
    for (int i = 0; i < n; i++){
        if (i) putchar(' ');
        printf("%lld", res[i]);
    }
    putchar('\n');
    free(a); free(res);
    return 0;
}
"""

S_2025_41_SOLUTION = """## 考点

一次遍历 + 后缀信息（王道 2 顺序表）。2025 新题：把"对每个 i 找后面最优配对"压缩成一遍扫描。

## 思路

res[i] = max{ A[i]×A[j] | i ≤ j ≤ n−1 }。因为可以选 j=i，只需维护从 i 到末尾的：

- **后缀最大值 mx**：A[i] ≥ 0 时，乘它最大；
- **后缀最小值 mn**：A[i] < 0 时，负数乘最小值最大。

从右向左扫描，先更新 mx/mn（含自身），再填 res[i]。

## 复杂度

时间 O(n)，额外空间 O(1)（输出数组不计）。正解"时间和空间尽可能高效"的满分写法就是这版。

## 考场提示

- A[i] = 0 时乘谁都是 0，归到哪个分支均可；
- 注意 j 可以从 i 开始（包含自身），mx/mn 要先更新再计算；
- int 会溢出：10⁶ × 10⁶，考场上建议 long long/长整型说明。
"""

P_2025_41 = dict(
    code="real-2025-41", title="后缀乘积最大值", kind="exam", year=2025,
    exam_no="第41题", chapter="线性表", tags=["顺序表", "后缀最值", "一次遍历"],
    difficulty=2, importance=5,
    statement_md=(
        "设有两个长度均为 n 的一维整型数组 A 和 res。对数组 A 中的每个元素 A[i]，"
        "计算 A[i] 与 A[j]（0 ≤ i ≤ j ≤ n−1）乘积的**最大值**，保存到 res[i] 中。\n\n"
        "例如 A = {1, 4, −9, 6}，则 res = {6, 24, 81, 36}。"
        "请设计时间和空间上尽可能高效的算法，输出 res 的全部元素。"
    ),
    input_md="第一行一个整数 n（1 ≤ n ≤ 10⁵）。\n第二行 n 个整数（|A[i]| ≤ 10⁶）。",
    output_md="输出一行 n 个整数：res[0..n-1]，用空格分隔。",
    samples=[{"input": "4\n1 4 -9 6\n", "output": "6 24 81 36\n"},
             {"input": "3\n-2 -3 -1\n", "output": "6 9 1\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 提示：从右往左维护后缀最大值与后缀最小值 */\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n    return 0;\n}\n"),
    ref_c=S_2025_41_REF_C,
    gen=gen_2025_41, ref_py=ref_2025_41,
    solution_md=S_2025_41_SOLUTION,
)

# ============================================================
# 2026-41 BST 与 K 差绝对值最小的结点
# ============================================================
def gen_2026_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 30)
        vals = rng.sample(range(-100, 101), n)
        k = rng.randint(-120, 120)
        cases.append(f"{n} {k}\n{ints_line(vals)}")
    n = 50000
    vals = rng.sample(range(-10**7, 10**7), n)
    k = rng.randint(-10**7, 10**7)
    cases.append(f"{n} {k}\n{ints_line(vals)}")
    return cases


def ref_2026_41(case):
    toks = case.split()
    n, k = int(toks[0]), int(toks[1])
    vals = [int(x) for x in toks[2:2 + n]]
    best = min(abs(v - k) for v in vals)
    ks = sorted(v for v in vals if abs(v - k) == best)
    return f"{best}\n{' '.join(map(str, ks))}\n"


S_2026_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

typedef struct BSTNode {
    int data;
    struct BSTNode *left, *right;
} BSTNode;

static BSTNode* insert(BSTNode *t, int v){
    if (!t){
        BSTNode *p = (BSTNode*)malloc(sizeof(BSTNode));
        p->data = v; p->left = p->right = NULL;
        return p;
    }
    if (v < t->data) t->left = insert(t->left, v);
    else if (v > t->data) t->right = insert(t->right, v);
    return t;
}

static long K, best;

/* 第一趟：求最小差值 */
static void find_best(BSTNode *t){
    if (!t) return;
    long d = t->data - K; if (d < 0) d = -d;
    if (d < best) best = d;
    find_best(t->left);
    find_best(t->right);
}

/* 第二趟：中序收集所有差值等于 best 的关键字（升序） */
static int first = 1;
static void collect(BSTNode *t){
    if (!t) return;
    collect(t->left);
    long d = t->data - K; if (d < 0) d = -d;
    if (d == best){
        if (!first) putchar(' ');
        printf("%d", t->data);
        first = 0;
    }
    collect(t->right);
}

int main(void){
    int n;
    if (scanf("%d %ld", &n, &K) != 2) return 0;
    BSTNode *root = NULL;
    for (int i = 0; i < n; i++){
        int v; scanf("%d", &v);
        root = insert(root, v);
    }
    best = LONG_MAX;
    find_best(root);
    printf("%ld\n", best);
    collect(root);
    putchar('\n');
    return 0;
}
"""

S_2026_41_SOLUTION = """## 考点

二叉搜索树的遍历与查找（王道 5.4）。2026 年最新题：**BST 全体结点中 |key−K| 最小的（可能有多个）**。

## 思路

思路一（通用）：全树遍历一次求最小差值 best，再中序遍历一遍输出所有差值等于 best 的结点（中序天然升序）。

思路二（利用 BST 性质）：查找 K 的过程中就能确定差值下界 —— 沿查找路径遇到的最近结点，与其相邻的前驱/后继即候选；但"所有"达到最小值的结点可能成对出现（正好卡在相邻关键字中间），稳妥考场上用两遍遍历最不易错。

## 复杂度

时间 O(n)，空间 O(h)。使用 BST 查找剪枝可到 O(h) 求差值下界，但收集全部仍 O(n)。

## 考场提示

- 建树用 BST 插入：小于走左、大于走右（本题关键字互异）；
- 差值绝对值用 long 防溢出；最小值初始化用一个极大哨兵；
- 输出 "先差值行，再升序关键字行"，关键字间空格分隔。
"""

P_2026_41 = dict(
    code="real-2026-41", title="BST 中与 K 差值最小的关键字", kind="exam", year=2026,
    exam_no="第41题", chapter="树与二叉树", tags=["二叉搜索树", "中序遍历"],
    difficulty=2, importance=5,
    statement_md=(
        "假定二叉搜索树使用二叉链表存储。给一棵二叉搜索树 T 和整数 K，"
        "查找树中关键字与 K 之差的**绝对值最小**的所有结点，输出该绝对值与这些结点中的关键字。\n\n"
        "评测输入给出 BST 的**插入序列**（关键字互不相同），按序列逐个插入构成 BST。"
    ),
    input_md=(
        "第一行两个整数 n（1 ≤ n ≤ 5×10⁴）和 K。\n"
        "第二行 n 个互不相同的整数，为 BST 的插入序列。"),
    output_md=(
        "第一行输出最小差值 d。\n"
        "第二行升序输出所有满足 |key−K| = d 的关键字，空格分隔。"),
    samples=[{"input": "5 7\n4 2 6 1 3\n", "output": "1\n6\n"},
             {"input": "4 5\n2 4 6 8\n", "output": "1\n4 6\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct BSTNode {\n    int data;\n"
        "    struct BSTNode *left, *right;\n} BSTNode;\n\n"
        "BSTNode* insert(BSTNode *t, int v);\n\n"
        "int main(void){\n    int n; long K;\n    scanf(\"%d %ld\", &n, &K);\n"
        "    /* TODO: 建树 -> 求最小差值 -> 中序收集 */\n    return 0;\n}\n"),
    ref_c=S_2026_41_REF_C,
    gen=gen_2026_41, ref_py=ref_2026_41,
    solution_md=S_2026_41_SOLUTION,
)

PROBLEMS = [P_2022_41, P_2023_41, P_2024_41, P_2025_41, P_2026_41]
