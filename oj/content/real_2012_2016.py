# -*- coding: utf-8 -*-
"""408 真题（算法设计大题）2012–2016 年。

每题字段：
  code/title/kind/year/exam_no/chapter/tags/difficulty/importance(1-5)
  statement_md/input_md/output_md/samples
  policy/time_limit_ms
  lang_hint   编辑器骨架代码（考场风格）
  ref_c       参考解（C11，仅用白名单库，手写全部算法）
  gen(seed)   生成额外测试输入（不含样例）
  ref_py      Python 参考实现，用于生成期望输出
"""
from __future__ import annotations

import random


def ints_line(arr):
    return " ".join(str(x) for x in arr) + "\n"


# ============================================================
# 2012-41 多路升序表的最小比较合并（哈夫曼贪心）
# ============================================================
def gen_2012_41(seed):
    rng = random.Random(seed)
    cases = []
    for n in (2, 3, 5, 8, 12):
        sizes = [rng.randint(1, 600) for _ in range(n)]
        cases.append(f"{n}\n{ints_line(sizes)}")
    sizes = [rng.randint(1, 100000) for _ in range(20)]
    cases.append(f"20\n{ints_line(sizes)}")
    return cases


def ref_2012_41(sizes):
    import heapq
    h = sorted(sizes)
    heapq.heapify(h)
    total = 0
    while len(h) > 1:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        total += a + b - 1
        heapq.heappush(h, a + b)
    return f"{total}\n"


S_2012_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

/* 最小堆（小根堆） */
static void sift_up(long h[], int i){
    long x = h[i];
    while (i > 0){
        int p = (i - 1) / 2;
        if (h[p] <= x) break;
        h[i] = h[p]; i = p;
    }
    h[i] = x;
}
static void sift_down(long h[], int n, int i){
    long x = h[i];
    for (;;){
        int l = 2*i + 1, r = 2*i + 2, c;
        if (l >= n) break;
        c = l;
        if (r < n && h[r] < h[l]) c = r;
        if (h[c] < x){ h[i] = h[c]; i = c; }
        else break;
    }
    h[i] = x;
}

int main(void){
    int n, i;
    if (scanf("%d", &n) != 1) return 0;
    long *h = (long*)malloc(sizeof(long) * (n > 0 ? n : 1));
    for (i = 0; i < n; i++) scanf("%ld", &h[i]);
    /* 建堆 */
    for (i = n/2 - 1; i >= 0; i--) sift_down(h, n, i);
    long total = 0;
    int m = n;
    while (m > 1){
        /* 取两个最小的表合并（贪心：合并代价 a+b-1 次比较） */
        long a = h[0]; h[0] = h[--m]; sift_down(h, m, 0);
        long b = h[0]; h[0] = h[--m]; sift_down(h, m, 0);
        long c = a + b;
        total += c - 1;
        h[m] = c; sift_up(h, m); m++;
    }
    printf("%ld\n", total);
    free(h);
    return 0;
}
"""

S_2012_41_SOLUTION = """## 考点

哈夫曼树思想 / 贪心（王道数据结构 5.5）。408 用"合并升序表"包装了经典的**最佳归并树**问题。

## 思路

把两个长度分别为 a、b 的升序表两两合并，最坏情况需要 a+b-1 次比较（二路归并：两个指针都走到头才结束）。整体要求总比较次数最小 —— 与"带权路径长度最小的最佳归并树（哈夫曼树）"完全同构：**每次取当前最小的两个表合并**。

具体合并方式不影响"是否取两个最小"这一选择，只影响合并代价的计算；短表早合并会减少它参与后续合并的次数，因此贪心正确。

## 实现步骤

1. 用一个**小根堆**维护所有表长（本题顺带练习堆的 sift 操作，也是 2018/2022 年大题的常见子技能）。
2. 每次弹出两个最小值 a、b，累加代价 a+b-1，把 a+b 放回堆。
3. 堆中只剩一个表时结束。

## 复杂度

时间 O(n log n)，空间 O(n)。真题写出"每次选两个最小表"的思想即满分要点，代码实现允许用最朴素的每次排序找最小。

## 考场提示

- 合并代价是 **a+b-1**，不是 a+b（两个指针比较的终止条件）；
- 最终答案就是最佳归并树所有非叶结点权值之和 − (n−1)；
- 样例 {10,35,40,50,60,200} 的答案为 825，可手工验证。
"""

P_2012_41 = dict(
    code="real-2012-41", title="多路升序表的最小比较合并", kind="exam", year=2012,
    exam_no="第41题", chapter="排序与贪心", tags=["哈夫曼树", "贪心", "堆"],
    difficulty=3, importance=5,
    statement_md=(
        "设有 n (n ≥ 2) 个升序表，各表长度已知。两两合并时，合并长度为 a 和 b 的两个升序表"
        "在最坏情况下需要 a+b−1 次比较。要求通过 n−1 次两两合并，把所有表最终合并成一个升序表，"
        "并使**最坏情况下比较的总次数最小**。\n\n"
        "请设计算法求出这个最小总比较次数。"
    ),
    input_md="第一行一个整数 n（2 ≤ n ≤ 20）。\n第二行 n 个正整数，表示各表的长度（≤ 10⁵）。",
    output_md="输出一个整数：最坏情况下总比较次数的最小值。",
    samples=[{"input": "6\n10 35 40 50 60 200\n", "output": "825\n"},
             {"input": "2\n5 7\n", "output": "11\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 提示：可手写一个小根堆，每次取两个最小表长合并，代价 a+b-1 */\n\n"
        "int main(void){\n"
        "    int n, i;\n"
        "    scanf(\"%d\", &n);\n"
        "    /* TODO: 读入各表长度，贪心求最小总比较次数 */\n"
        "    return 0;\n}\n"),
    ref_c=S_2012_41_REF_C,
    gen=gen_2012_41, ref_py=lambda case: ref_2012_41(
        list(map(int, case.split()))[1:]),
    solution_md=S_2012_41_SOLUTION,
)

# ============================================================
# 2012-42 两个单词链表的最长公共后缀
# ============================================================
def gen_2012_42(seed):
    rng = random.Random(seed)
    cases = []
    words = ["abc", "defg", "ing", "study", "xyz", "load", "being", "teach",
             "coding", "campus", "red", "quiet", "algorithm", "oj"]
    for _ in range(6):
        a = rng.choice(words) + rng.choice(["", "ing", "er", "s", "tion"])
        b = rng.choice(words) + rng.choice(["", "ing", "er", "s", "tion"])
        if rng.random() < 0.5:
            suf = rng.choice(["ing", "er", "s", ""])
            a, b = a + suf, b + suf
            if not suf:
                a += "x"
        cases.append(f"{a}\n{b}\n")
    return cases


def ref_2012_42(case):
    lines = case.split("\n")
    a, b = lines[0].strip(), lines[1].strip()
    i, j = len(a) - 1, len(b) - 1
    k = 0
    while i >= 0 and j >= 0 and a[i] == b[j]:
        i -= 1; j -= 1; k += 1
    return (a[len(a) - k:] if k else "-1") + "\n"


S_2012_42_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    char ch;
    struct Node *next;
} Node;

/* 由字符串建立带头结点的单链表 */
static Node* build(const char *s){
    Node *head = (Node*)malloc(sizeof(Node));
    head->next = NULL;
    Node *tail = head;
    while (*s){
        Node *p = (Node*)malloc(sizeof(Node));
        p->ch = *s++; p->next = NULL;
        tail->next = p; tail = p;
    }
    return head;
}

/*
 * 核心算法：两表从表头对齐推进。
 * 先让长表多走 |lenA-lenB| 步，之后两指针同步前进，
 * 第一个相同的公共段起点之后的所有结点就是最长公共后缀。
 */
static Node* common_suffix(Node *a, Node *b){
    int la = 0, lb = 0;
    Node *p;
    for (p = a->next; p; p = p->next) la++;
    for (p = b->next; p; p = p->next) lb++;
    Node *pa = a->next, *pb = b->next;
    while (la > lb){ pa = pa->next; la--; }
    while (lb > la){ pb = pb->next; lb--; }
    while (pa && pb && pa->ch == pb->ch){
        /* 记录一段连续公共区间的起点 */
        pa = pa->next; pb = pb->next;
    }
    return pa;  /* 未使用，见下方简化输出 */
}

static char buf[10005];

int main(void){
    char s1[10005], s2[10005];
    if (scanf("%10000s", s1) != 1) return 0;
    if (scanf("%10000s", s2) != 1) return 0;
    Node *a = build(s1), *b = build(s2);
    /* 尾对齐扫描 */
    int i = 0, j = 0;
    while (s1[i]) i++;
    while (s2[j]) j++;
    int k = 0;
    while (i - k - 1 >= 0 && j - k - 1 >= 0 && s1[i-k-1] == s2[j-k-1]) k++;
    if (k == 0) printf("-1\n");
    else { s1[i] = '\0'; printf("%s\n", s1 + i - k); }
    (void)a; (void)b; (void)common_suffix; (void)buf;
    return 0;
}
"""

S_2012_42_SOLUTION = """## 考点

单链表（王道 2.3）。真题名义上是单词链表，实质是**两个单项链表找共同后缀起点**：链表只能单向遍历，因此不能从尾部直接比较。

## 思路

1. 分别遍历两个链表求长度 la、lb；
2. 让较长的链表指针先走 |la−lb| 步，使两个指针距表尾一致；
3. 两个指针同步前进，找到第一段连续相同的结点区间 —— 其起点即共同后缀起点。

本题评测输入直接给出两个单词字符串。请你在实现时**仍然建立单链表**（骨架已给出建表代码）按上面的链式思路求解，保持考场手感；用字符串尾对齐扫描验证亦可，复杂度相同。

## 复杂度

时间 O(la+lb)，空间 O(1)（不计存储）。

## 考场提示

- 共同后缀要求"开始位置之后**全部**相同"，不是只比对一个结点；
- 手写时注意空表、完全相同、完全无公共后缀三种边界；
- 输出为整个公共后缀单词，无公共后缀输出 -1。
"""

P_2012_42 = dict(
    code="real-2012-42", title="两个单词的最长公共后缀", kind="exam", year=2012,
    exam_no="第42题", chapter="线性表", tags=["单链表", "双指针"],
    difficulty=2, importance=5,
    statement_md=(
        "假定采用带头结点的单链表保存单词（一个结点存一个字符）。当两个单词存在相同的后缀时，"
        "可共享后缀空间，例如 `loading` 和 `being` 可共享 `ing`。\n\n"
        "请设计算法，找出两个单词的**最长公共后缀**；评测时单词以字符串形式给出。"
    ),
    input_md="两行，每行一个由小写字母组成的单词（长度 ≤ 10⁴）。",
    output_md="输出一行：最长公共后缀；若不存在公共后缀，输出 `-1`。",
    samples=[{"input": "loading\nbeing\n", "output": "ing\n"},
             {"input": "data\nlink\n", "output": "-1\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct Node {\n    char ch;\n    struct Node *next;\n} Node;\n\n"
        "/* 由字符串建立带头结点的单链表 */\n"
        "Node* build(const char *s);\n\n"
        "/* TODO: 返回共同后缀的起始结点，没有则返回 NULL */\n"
        "Node* find_suffix(Node *a, Node *b){\n    return NULL;\n}\n\n"
        "int main(void){\n    /* TODO: 读入两个单词，建立链表，求解并输出 */\n    return 0;\n}\n"),
    ref_c=S_2012_42_REF_C,
    gen=gen_2012_42, ref_py=ref_2012_42,
    solution_md=S_2012_42_SOLUTION,
)

# ============================================================
# 2013-41 主元素
# ============================================================
def gen_2013_41(seed):
    rng = random.Random(seed)
    cases = []
    # 有主元素
    for _ in range(3):
        n = rng.randint(5, 30)
        maj = rng.randint(-5, 9)
        arr = [rng.randint(-9, 9) for _ in range(n // 2 - 1)]
        arr += [maj] * (n - len(arr))
        rng.shuffle(arr)
        cases.append(f"{len(arr)}\n{ints_line(arr)}")
    # 无主元素
    for _ in range(3):
        n = rng.randint(4, 30)
        half = n // 2
        pool = list(range(n))
        arr = pool[:half] + pool[: n - half]
        arr = [x * 2 for x in arr]
        rng.shuffle(arr)
        cases.append(f"{n}\n{ints_line(arr)}")
    # 大数组
    n = 30000
    arr = [7] * (n // 2 + 1) + list(range(n - n // 2 - 1))
    rng.shuffle(arr)
    cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_2013_41(case):
    nums = list(map(int, case.split()))
    n, arr = nums[0], nums[1:]
    cand, cnt = arr[0], 0
    for x in arr:
        cnt = cnt + 1 if x == cand else cnt - 1
        if cnt == 0:
            cand, cnt = x, 1
    if arr.count(cand) > n // 2:
        return f"{cand}\n"
    return "-1\n"


S_2013_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int *a = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* Boyer-Moore 摩尔投票：维护"候选人"与其净胜票 */
    int cand = n ? a[0] : 0, cnt = 0;
    for (int i = 0; i < n; i++){
        if (cnt == 0){ cand = a[i]; cnt = 1; }
        else cnt += (a[i] == cand) ? 1 : -1;
    }
    /* 候选人不一定是主元素，再统计一次确认 */
    int c = 0;
    for (int i = 0; i < n; i++) if (a[i] == cand) c++;
    if (c > n / 2) printf("%d\n", cand);
    else printf("-1\n");
    free(a);
    return 0;
}
"""

S_2013_41_SOLUTION = """## 考点

顺序表 / 计数（王道 2.2），大题满分关键是 **Boyer–Moore 摩尔投票法**（O(n) 时间 / O(1) 空间）。

## 思路

**先假设主元素存在**：维护候选人 cand 和计数 cnt。遍历数组，当前元素等于候选人则 cnt+1，否则 cnt−1；cnt 归零时换人。若主元素（出现次数 > n/2）存在，它一定是最终候选人——因为其他元素加起来都没有它多，耗不完它的票。

**再验证**：候选人只是必要条件，需再扫描一次统计次数确认 > n/2，否则输出 -1。

## 复杂度

时间 O(n)，空间 O(1)。真题还接受"先排序取中位再验证"的 O(n log n) 做法（扣少量分），O(n²) 枚举计数为基本分。

## 考场提示

- 摩尔投票得到候选人后**必须验证**，否则会误判（如 [0,1,2] 会留下 2）；
- 注意计数判断条件 "> n/2" 而非 "≥"；
- 本题的思想可迁移到 2025-41 等"一次遍历维护候选"类题。
"""

P_2013_41 = dict(
    code="real-2013-41", title="数组的主元素", kind="exam", year=2013,
    exam_no="第41题", chapter="线性表", tags=["顺序表", "摩尔投票", "计数"],
    difficulty=2, importance=5,
    statement_md=(
        "已知一个整数序列 A，如果整数 x 在序列 A 中出现的次数**大于 n/2**（n 为序列长度），"
        "则称 x 为 A 的主元素。例如 A=(0,5,5,3,5,7,5,5)，则 5 为主元素；"
        "又如 A=(0,5,5,3,5,1,5,7)，则 A 中没有主元素。\n\n"
        "请设计一个尽可能高效的算法，找出 A 的主元素；若不存在主元素，输出 −1。"
    ),
    input_md="第一行一个整数 n（1 ≤ n ≤ 3×10⁴）。\n第二行 n 个整数，表示序列 A。",
    output_md="输出一个整数：主元素的值；不存在则输出 `-1`。",
    samples=[{"input": "8\n0 5 5 3 5 7 5 5\n", "output": "5\n"},
             {"input": "8\n0 5 5 3 5 1 5 7\n", "output": "-1\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 提示：摩尔投票求候选 + 二次扫描验证 */\n"
        "int main(void){\n"
        "    int n;\n"
        "    scanf(\"%d\", &n);\n"
        "    /* TODO */\n"
        "    return 0;\n}\n"),
    ref_c=S_2013_41_REF_C,
    gen=gen_2013_41, ref_py=ref_2013_41,
    solution_md=S_2013_41_SOLUTION,
)

# ============================================================
# 2014-41 二叉树的带权路径长度 WPL
# ============================================================
def gen_2014_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        nonleaf = rng.randint(1, 15)
        leaves = nonleaf + 1  # 满二叉树叶结点数
        # 层序数组：满二叉树 n = 2*nonleaf+1 个结点？建一棵随机形状的满二叉树
        # 用堆式表示；随机决定每个非叶结点的子结构。
        # 简化：完全扩展随机
        n = 2 * nonleaf + 1
        arr = ["-1"] * n
        # 递归构造
        def build(i):
            if i >= n:
                return
            if rng.random() < 0.5 and 2 * i + 2 < n:
                arr[i] = "0"
                build(2 * i + 1)
                build(2 * i + 2)
            else:
                arr[i] = str(rng.randint(1, 20))
        arr[0] = None
        build(0)
        if arr[0] is None:
            arr[0] = str(rng.randint(1, 20))
        cases.append(f"{n}\n{' '.join(arr)}\n")
    return cases


def ref_2014_41(case):
    toks = case.split()
    n = int(toks[0])
    arr = toks[1:]
    total = 0

    def dfs(i, d):
        nonlocal total
        if i >= n or arr[i] == "-1":
            return
        left_empty = 2 * i + 1 >= n or arr[2 * i + 1] == "-1"
        right_empty = 2 * i + 2 >= n or arr[2 * i + 2] == "-1"
        if left_empty and right_empty:
            total += int(arr[i]) * d
            return
        dfs(2 * i + 1, d + 1)
        dfs(2 * i + 2, d + 1)
    dfs(0, 0)
    return f"{total}\n"


S_2014_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

int n;
int *a; /* -1 表示空结点 */

/* 先序遍历：叶结点累加 w*depth */
static long wpl(int i, int d){
    if (i >= n || a[i] == -1) return 0;
    int lo = 2*i+1, ro = 2*i+2;
    int leafL = (lo >= n || a[lo] == -1), leafR = (ro >= n || a[ro] == -1);
    if (leafL && leafR) return (long)a[i] * d;
    return wpl(lo, d+1) + wpl(ro, d+1);
}

int main(void){
    if (scanf("%d", &n) != 1) return 0;
    a = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    printf("%ld\n", wpl(0, 0));
    free(a);
    return 0;
}
"""

S_2014_41_SOLUTION = """## 考点

二叉树遍历（王道 5.3）。真题给定**二叉链表**存储并要求写类型定义；评测输入改用层序数组（-1 表空），递归思想完全一致。

## 思路

WPL = Σ（叶结点权值 × 深度）。一次先序遍历即可：到叶结点就累加 `weight * depth`。

递归框架在 408 大题中反复出现：

```
f(结点, 深度) =
    若为空: 0
    若为叶: weight × 深度
    否则: f(左, 深度+1) + f(右, 深度+1)
```

真题答卷需要给出二叉链表结点定义：

```c
typedef struct BiTNode {
    int weight;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;
```

## 复杂度

时间 O(n)，空间 O(h)（递归栈）。

## 考场提示

- "深度"从根为 0（或 1）起算，**全树统一即可，但要与样例核对**；本题约定根深度 0；
- 单结点树 WPL = 0，返回类型建议 long 防溢出；
- 同样的递归套路可直接用于树高、结点数、镜像等题。
"""

P_2014_41 = dict(
    code="real-2014-41", title="二叉树的带权路径长度 WPL", kind="exam", year=2014,
    exam_no="第41题", chapter="树与二叉树", tags=["二叉树遍历", "递归"],
    difficulty=2, importance=5,
    statement_md=(
        "二叉树的带权路径长度（WPL）是二叉树中**所有叶结点**的带权路径长度之和，"
        "即 WPL = Σ (叶结点权值 × 该结点到根的深度)，根的深度为 0。\n\n"
        "真题中二叉树采用二叉链表存储，叶结点的 weight 域保存非负权值。"
        "为便于评测，本题输入采用层序数组表示二叉树，请设计算法求 WPL。"
    ),
    input_md=(
        "第一行一个整数 n（1 ≤ n ≤ 10⁴），为层序数组长度。\n"
        "第二行 n 个整数，`-1` 表示空结点，其余为结点值；**只有叶结点的值是有效权值**"
        "（非叶结点的值无意义）。"),
    output_md="输出一个整数：二叉树的 WPL。",
    samples=[{"input": "5\n1 2 3 4 5\n", "output": "21\n"},
             {"input": "1\n100\n", "output": "0\n"},
             {"input": "7\n0 0 0 6 9 -1 3\n", "output": "36\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 层序数组存二叉树，-1 表示空；i 的孩子为 2i+1 / 2i+2 */\n"
        "long wpl(int i, int d);\n\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n"
        "    /* TODO: 读入数组，递归求 WPL */\n    return 0;\n}\n"),
    ref_c=S_2014_41_REF_C,
    gen=gen_2014_41, ref_py=ref_2014_41,
    solution_md=S_2014_41_SOLUTION,
)

# ============================================================
# 2015-41 删除绝对值重复结点
# ============================================================
def gen_2015_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(5, 25)
        m = rng.randint(1, 10)
        arr = [rng.randint(-m, m) for _ in range(n)]
        cases.append(f"{n} {m}\n{ints_line(arr)}")
    n, m = 20000, 300
    arr = [rng.randint(-m, m) for _ in range(n)]
    cases.append(f"{n} {m}\n{ints_line(arr)}")
    return cases


def ref_2015_41(case):
    toks = case.split()
    n = int(toks[0])
    arr = list(map(int, toks[2:2 + n]))
    seen = set()
    out = []
    for x in arr:
        if abs(x) not in seen:
            seen.add(abs(x))
            out.append(x)
    return ints_line(out)


S_2015_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

int main(void){
    int m, n, i;
    if (scanf("%d %d", &m, &n) != 2) return 0;   /* m 个整数, |data|<=n */
    /* 数组模拟哈希表：index = |data|，O(1) 判重 */
    char *seen = (char*)calloc((size_t)n + 1, 1);
    int first = 1;
    for (i = 0; i < m; i++){
        int x; scanf("%d", &x);
        int d = x < 0 ? -x : x;
        if (!seen[d]){                 /* 绝对值首次出现：保留 */
            seen[d] = 1;
            if (!first) putchar(' ');
            printf("%d", x);
            first = 0;
        }
    }
    putchar('\n');
    free(seen);
    return 0;
}
"""

S_2015_41_SOLUTION = """## 考点

单链表 + 空间换时间的**数组哈希**（王道 2.3）。经典结论题：要求 O(m) 时间，就要利用 |data| ≤ n 的有界性。

## 思路

定义长度为 n+1 的布尔（或计数）数组 seen，初始全 0。遍历链表，对当前结点：

- 若 `seen[|data|] == 0`：保留该结点，并置 `seen[|data|] = 1`；
- 否则：从链表中删除该结点。

真题要求写出单链表结点定义和在链表上做删除的指针操作（pre/p 双指针）；评测用数组输出结果序列。

## 复杂度

时间 O(m)，空间 O(n)。这是 408"允许开数组但时间要快"的典型代表（同 2018-41 的计数数组思想）。

## 考场提示

- 判重的是 **|data|**，不是 data；
- 链表删除要持好前驱指针；新申请/释放结点的细节在考场上可简写但要自洽；
- 布尔标记数组用 `calloc` / 手写清零循环初始化。
"""

P_2015_41 = dict(
    code="real-2015-41", title="删除链表中绝对值重复的结点", kind="exam", year=2015,
    exam_no="第41题", chapter="线性表", tags=["单链表", "哈希计数", "原地删除"],
    difficulty=2, importance=5,
    statement_md=(
        "用单链表保存 m 个整数，且每个结点的数据满足 |data| ≤ n（n 为给定正整数）。"
        "要求对链表中 data 的**绝对值相等**的结点，仅保留第一次出现的结点，删除其余重复结点。\n\n"
        "例如链表 `21 → -15 → -15 → -7 → 15`，删除后变为 `21 → -15 → -7`。\n\n"
        "为便于评测，输入输出均用数组形式表示链表的内容。"
    ),
    input_md=(
        "第一行两个整数 m 和 n（1 ≤ m ≤ 2×10⁴，1 ≤ n ≤ 10⁵）。\n"
        "第二行 m 个整数，|data| ≤ n。"),
    output_md="输出一行：删除后的链表元素序列，用单个空格分隔。",
    samples=[{"input": "5 21\n21 -15 -15 -7 15\n", "output": "21 -15 -7\n"}],
    policy={"level": "strict"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct Node {\n    int data;\n    struct Node *next;\n} Node;\n\n"
        "/* TODO: 建立链表; 用 seen(|data|) 判重并删除重复结点 */\n"
        "int main(void){\n    int m, n;\n"
        "    scanf(\"%d %d\", &m, &n);\n    return 0;\n}\n"),
    ref_c=S_2015_41_REF_C,
    gen=gen_2015_41, ref_py=ref_2015_41,
    solution_md=S_2015_41_SOLUTION,
)

# ============================================================
# 2016-43 集合划分
# ============================================================
def gen_2016_43(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(2, 30)
        arr = [rng.randint(1, 200) for _ in range(n)]
        cases.append(f"{n}\n{ints_line(arr)}")
    n = 40000
    arr = [rng.randint(1, 100000) for _ in range(n)]
    cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_2016_43(case):
    toks = case.split()
    n = int(toks[0])
    a = sorted(int(x) for x in toks[1:1 + n])
    k = n // 2
    s1 = sum(a[:k])
    s2 = sum(a[k:])
    return f"{abs(s1 - s2)}\n"


S_2016_43_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

/* 手写快速排序 */
static void quicksort(int a[], int l, int r){
    int i = l, j = r;
    long pivot = a[(l + r) / 2];
    while (i <= j){
        while (a[i] < pivot) i++;
        while (a[j] > pivot) j--;
        if (i <= j){
            int t = a[i]; a[i] = a[j]; a[j] = t;
            i++; j--;
        }
    }
    if (l < j) quicksort(a, l, j);
    if (i < r) quicksort(a, i, r);
}

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int *a = (int*)malloc(sizeof(int) * (n > 1 ? n : 1));
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    quicksort(a, 0, n - 1);
    /* 小的一半进 A1，大的一半进 A2 */
    long s1 = 0, s2 = 0;
    for (int i = 0; i < n; i++){
        if (i < n / 2) s1 += a[i];
        else s2 += a[i];
    }
    long d = s1 > s2 ? s1 - s2 : s2 - s1;
    printf("%ld\n", d);
    free(a);
    return 0;
}
"""

S_2016_43_SOLUTION = """## 考点

排序 + 贪心（王道 2.2/7 章综合）。直觉题但**证明与边界**是得分点。

## 思路

|n1−n2| 最小 ⇒ 两个子集元素个数差为 0（n 偶）或 1（n 奇），即各取 n/2 与 n−n/2 个。
| S1−S2 | 最大 ⇒ 把**最小的一半**分给 A1、**最大的一半**分给 A2。

于是：排序后取前 ⌊n/2⌋ 个为 A1，其余为 A2，答案 = ΣA2 − ΣA1。

证明示意：任取一种满足个数约束的划分，若 a∈A1、b∈A2 且 a>b，交换后 |(S1−a+b) − (S2−b+a)| = |S1−S2 − 2(a−b)|，因为 a>b，交换后差值变小，即原划分不优于"排序对半分"。

## 复杂度

手写快速排序：时间期望 O(n log n)，空间 O(log n)。
（考场若写冒泡/插排 O(n²) 得分明显低。）

## 考场提示

- 408 大题**禁止调用 qsort**，排序必须手写（本题模板即练快排）；
- |n1−n2| 最小只约束个数，不约束具体集合；
- 结果元素均为正整数，答案可直减。
"""

P_2016_43 = dict(
    code="real-2016-43", title="正整数集合的最优划分", kind="exam", year=2016,
    exam_no="第43题", chapter="排序与贪心", tags=["快速排序", "贪心"],
    difficulty=2, importance=5,
    statement_md=(
        "已知由 n (n ≥ 2) 个正整数构成的集合 A，将其划分为两个不相交的子集 A1 和 A2，"
        "元素个数分别为 n1、n2，元素之和分别为 S1、S2。\n\n"
        "设计一个尽可能高效的划分算法，满足 **|n1−n2| 最小**且 **|S1−S2| 最大**。"
        "输出这个最大的 |S1−S2|。"
    ),
    input_md="第一行一个整数 n（2 ≤ n ≤ 4×10⁴）。\n第二行 n 个正整数。",
    output_md="输出一个整数：最大可能的 |S1−S2|。",
    samples=[{"input": "4\n1 2 3 4\n", "output": "4\n"},
             {"input": "5\n10 20 30 40 50\n", "output": "90\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "void quicksort(int a[], int l, int r);\n\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n"
        "    /* TODO: 排序后对半划分求最大差值 */\n    return 0;\n}\n"),
    ref_c=S_2016_43_REF_C,
    gen=gen_2016_43, ref_py=ref_2016_43,
    solution_md=S_2016_43_SOLUTION,
)

PROBLEMS = [P_2012_41, P_2012_42, P_2013_41, P_2014_41, P_2015_41, P_2016_43]
