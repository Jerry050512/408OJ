# -*- coding: utf-8 -*-
"""408 真题 2017–2021（第 41 题算法设计）。"""
from __future__ import annotations

import random


def ints_line(arr):
    return " ".join(str(x) for x in arr) + "\n"


# ============================================================
# 2017-41 表达式树转中缀表达式
# ============================================================
def gen_2017_41(seed):
    rng = random.Random(seed)
    cases = []

    def rand_expr(depth):
        if depth == 0 or rng.random() < 0.3:
            return rng.choice(list("abcde") + [str(rng.randint(1, 9))])
        op = rng.choice("+-*/")
        return (rand_expr(depth - 1), op, rand_expr(depth - 1))

    def level_order(t):
        # 层序队列，# 补满到叶子的孩子
        from collections import deque
        out = []
        q = deque([t])
        while q:
            node = q.popleft()
            if node is None:
                out.append("#")
            else:
                if isinstance(node, tuple):
                    out.append(node[1])
                    q.append(node[0])
                    q.append(node[2])
                else:
                    out.append(node)
        # 去尾部 #
        while out and out[-1] == "#":
            out.pop()
        return out

    for _ in range(8):
        t = rand_expr(3)
        toks = level_order(t)
        cases.append(f"{len(toks)}\n{' '.join(toks)}\n")
    # 单操作数
    cases.append("1\nx\n")
    return cases


def ref_2017_41(case):
    toks = case.split()
    n = int(toks[0])
    arr = toks[1:]

    def is_op(x):
        return x in "+-*/"

    def build(i):
        if i >= n or arr[i] == "#":
            return None
        return (arr[i], build(2 * i + 1), build(2 * i + 2))

    def to_infix(node, is_root):
        if node is None:
            return ""
        v, l, r = node
        if not is_op(v):
            return v
        s = to_infix(l, False) + v + to_infix(r, False)
        return s if is_root else "(" + s + ")"

    return to_infix(build(0), True) + "\n"


S_2017_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    char data[12];
    struct Node *left, *right;
} Node;

static int is_op(const char *s){
    return (s[0]=='+'||s[0]=='-'||s[0]=='*'||s[0]=='/') && s[1]=='\0';
}

static char (*g_tok)[12];
static int g_n;

static Node* build(int i){
    if (i >= g_n || strcmp(g_tok[i], "#") == 0) return NULL;
    Node *p = (Node*)malloc(sizeof(Node));
    strcpy(p->data, g_tok[i]);
    p->left = build(2*i+1);
    p->right = build(2*i+2);
    return p;
}

/* 中缀输出：除根以外的每个非叶子树都加括号 */
static void to_infix(Node *t, int is_root){
    if (!t) return;
    if (!is_op(t->data)){ fputs(t->data, stdout); return; }
    if (!is_root) putchar('(');
    to_infix(t->left, 0);
    fputs(t->data, stdout);
    to_infix(t->right, 0);
    if (!is_root) putchar(')');
}

int main(void){
    int n, i;
    if (scanf("%d", &n) != 1) return 0;
    g_n = n;
    g_tok = malloc((size_t)(n > 0 ? n : 1) * sizeof *g_tok);
    for (i = 0; i < n; i++) scanf("%11s", g_tok[i]);
    Node *root = build(0);
    to_infix(root, 1);
    putchar('\n');
    return 0;
}
"""

S_2017_41_SOLUTION = """## 考点

二叉树的递归应用（王道 5.3），把"中缀表达式加括号"翻译成树上规则：**中序遍历 + 子树括号**。

## 思路

- 叶结点（操作数）：直接输出；
- 非叶结点（操作符）：输出 `(` 左子树表达式 操作符 右子树表达式 `)`；
- **根结点不加最外层括号**。

判断"操作符还是操作数"：结点字符串为单个 +-*/ 即操作符。本题输入的层序序列中，操作数只占叶位置（除单结点树）。

## 复杂度

建伦敦 O(n)? 建树 O(n)（每个数组元素恰好一次），输出 O(n)。

## 考场提示

- 真题结点结构 `char data[10]`，用 `strcpy` 复制；评测骨架已建好树，专注递归输出；
- 若题目给的一元负号结点（只有一个孩子），要按"操作符只有一个操作数"另行处理 —— 本题输入保证满二叉（操作符均有两个孩子）；
- 括号规则容易写成"所有非叶都加括号"，注意根是例外。
"""

P_2017_41 = dict(
    code="real-2017-41", title="表达式树转中缀表达式", kind="exam", year=2017,
    exam_no="第41题", chapter="树与二叉树", tags=["二叉树遍历", "表达式树", "递归"],
    difficulty=3, importance=5,
    statement_md=(
        "设计一个算法，将给定的表达式树（二叉树）转换为等价的中缀表达式"
        "（通过括号反映操作符的计算次序）并输出。\n\n"
        "规则：叶结点（操作数）直接输出；非叶结点（操作符）输出其左子树、操作符、右子树，"
        "并用一对括号括起整个子表达式；**根结点最外层不加括号**。\n\n"
        "真题采用二叉链表存储（`char data[10]` 存操作数或操作符）。"
        "评测输入用层序序列表示表达式树：操作符为单个字符 `+ - * /`，"
        "操作数为单个字母或数字；`#` 表示空结点。输入保证每个操作符恰有两个孩子。"
    ),
    input_md=(
        "第一行一个整数 n（1 ≤ n ≤ 2047）。\n"
        "第二行 n 个用空格分隔的记号（操作符 / 操作数 / `#`），构成二叉树的层序表示。"),
    output_md="输出一行：转换得到的中缀表达式（不含空格）。",
    samples=[{"input": "7\n* + - a b c d\n", "output": "(a+b)*(c-d)\n"},
             {"input": "1\nx\n", "output": "x\n"},
             {"input": "7\n+ * - a b c d\n", "output": "(a*b)+(c-d)\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
        "typedef struct Node {\n    char data[12];\n"
        "    struct Node *left, *right;\n} Node;\n\n"
        "/* TODO: 由层序记号建树（# 为空），递归输出中缀表达式 */\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n    return 0;\n}\n"),
    ref_c=S_2017_41_REF_C,
    gen=gen_2017_41, ref_py=ref_2017_41,
    solution_md=S_2017_41_SOLUTION,
)

# ============================================================
# 2018-41 未出现的最小正整数
# ============================================================
def gen_2018_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 30)
        arr = [rng.randint(-3, n + 2) for _ in range(n)]
        cases.append(f"{n}\n{ints_line(arr)}")
    n = 50000
    arr = list(range(2, n + 2))  # 缺 1
    rng.shuffle(arr)
    cases.append(f"{n}\n{ints_line(arr)}")
    arr = list(range(1, n + 1))  # 缺 n+1
    rng.shuffle(arr)
    cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_2018_41(case):
    toks = case.split()
    n = int(toks[0])
    a = [int(x) for x in toks[1:1 + n]]
    seen = [0] * (n + 2)
    for x in a:
        if 1 <= x <= n:
            seen[x] = 1
    for i in range(1, n + 2):
        if not seen[i]:
            return f"{i}\n"
    return f"{n + 1}\n"


S_2018_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    /* 答案一定在 [1, n+1] 内：开一个 n+1 的计数数组 */
    char *seen = (char*)calloc((size_t)n + 2, 1);
    for (int i = 0; i < n; i++){
        int x; scanf("%d", &x);
        if (x >= 1 && x <= n) seen[x] = 1;
    }
    for (int i = 1; i <= n + 1; i++){
        if (!seen[i]){ printf("%d\n", i); break; }
    }
    free(seen);
    return 0;
}
"""

S_2018_41_SOLUTION = """## 考点

顺序表 / 计数数组（王道 2.2），思想与 2015-41 的 seen 数组同族：**值有界 => 用下标当哈希**。

## 思路

抽屉原理：n 个整数中未出现的**最小正整数**一定 ∈ [1, n+1]。开一个长度为 n+1 的标记数组，把出现过的、且落在 [1,n] 的值打钩，最后从小到大找第一个没落钩的下标即为答案。

## 复杂度

时间 O(n)，空间 O(n)。若要求 O(1) 空间，可以"原地置换"把 x 放到下标 x-1 —— 考场上写标记数组即可。

## 考场提示

- 负数与 0 直接忽略；
- 大于 n 的值对答案无影响（它们占不掉 [1,n+1] 全部位置时一定有空缺）；
- 记得输出的是下标 i，不是计数。
"""

P_2018_41 = dict(
    code="real-2018-41", title="数组中未出现的最小正整数", kind="exam", year=2018,
    exam_no="第41题", chapter="线性表", tags=["顺序表", "哈希计数"],
    difficulty=1, importance=5,
    statement_md=(
        "给定一个含 n (n ≥ 1) 个整数的数组，设计一个时间上尽可能高效的算法，"
        "找出数组中未出现的**最小正整数**。\n\n"
        "例如数组 {-5, 3, 2, 3} 中未出现的最小正整数是 1；数组 {1, 2, 3} 中未出现的最小正整数是 4。"
    ),
    input_md="第一行一个整数 n（1 ≤ n ≤ 5×10⁴）。\n第二行 n 个整数。",
    output_md="输出一个整数：未出现的最小正整数。",
    samples=[{"input": "4\n-5 3 2 3\n", "output": "1\n"},
             {"input": "3\n1 2 3\n", "output": "4\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 提示：答案必在 [1, n+1]，用标记数组 */\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n"
        "    /* TODO */\n    return 0;\n}\n"),
    ref_c=S_2018_41_REF_C,
    gen=gen_2018_41, ref_py=ref_2018_41,
    solution_md=S_2018_41_SOLUTION,
)

# ============================================================
# 2019-41 链表重排 L1,Ln,L2,Ln-1...
# ============================================================
def gen_2019_41(seed):
    rng = random.Random(seed)
    cases = []
    for n in (1, 2, 3, 5, 8, 20):
        arr = [rng.randint(1, 99) for _ in range(n)]
        cases.append(f"{n}\n{ints_line(arr)}")
    n = 30000
    arr = [rng.randint(1, 100000) for _ in range(n)]
    cases.append(f"{n}\n{ints_line(arr)}")
    return cases


def ref_2019_41(case):
    toks = case.split()
    n = int(toks[0])
    a = [int(x) for x in toks[1:1 + n]]
    out = []
    for i in range(n):
        idx = i // 2 if i % 2 == 0 else n - 1 - i // 2
        out.append(a[idx])
    return ints_line(out)


S_2019_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;
} Node;

/* 求链表中点（偶数时返回前半最后一个结点） */
static Node* mid(Node *head){
    Node *s = head->next, *f = head->next;
    while (f->next && f->next->next){
        s = s->next;
        f = f->next->next;
    }
    return s;
}

/* 就地逆置（带头结点） */
static Node* reverse(Node *h){
    Node *prev = NULL, *cur = h;
    while (cur){
        Node *nx = cur->next;
        cur->next = prev;
        prev = cur; cur = nx;
    }
    return prev;
}

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    Node head; head.next = NULL;
    Node *tail = &head;
    for (int i = 0; i < n; i++){
        Node *p = (Node*)malloc(sizeof(Node));
        scanf("%d", &p->data);
        p->next = NULL; tail->next = p; tail = p;
    }
    /* 1) 找中点，截成两段 A=[1..k], B=[k+1..n]；2) B 逆置；3) 交替归并 */
    if (n > 1){
        Node *m = mid(&head);
        Node *b = reverse(m->next);
        m->next = NULL;
        Node *a = head.next;
        while (a && b){
            Node *na = a->next, *nb = b->next;
            a->next = b;
            if (na == NULL){ /* 避免环 */ b->next = NULL; break; }
            b->next = na;
            a = na; b = nb;
        }
    }
    int first = 1;
    for (Node *p = head.next; p; p = p->next){
        if (!first) putchar(' ');
        printf("%d", p->data);
        first = 0;
    }
    putchar('\n');
    return 0;
}
"""

S_2019_41_SOLUTION = """## 考点

单链表三部曲（王道 2.3）：**找中点 + 就地逆置 + 交替归并**。2019 年这套组合是链表大题的"满分模板"，务必烂熟。

## 思路

1. **找中点**：快慢指针，快指针每次两步；n 为偶数时慢指针落在前半最后一个结点。
2. **截断 + 逆置后半段**：把后半段链表就地逆置（头插法 / 三指针）。
3. **交替归并**：前半 p1 与逆置后的后半 p2 依次穿插挂接：p1→p2→p1.next→p2.next→…

## 复杂度

时间 O(n)，空间 O(1)（题目硬性要求）。

## 考场提示

- 三部曲每一步都要能**独立默写**：中点、逆置、归并都是其他大题的子技能；
- 注意 n=1、n=2 与奇偶的边界；
- 归并时切忌把尾部指针留成环，最后一段（前半段多一个结点时）单独收尾。
"""

P_2019_41 = dict(
    code="real-2019-41", title="单链表重排 L1→Ln→L2→Ln-1", kind="exam", year=2019,
    exam_no="第41题", chapter="线性表", tags=["单链表", "快慢指针", "就地逆置"],
    difficulty=3, importance=5,
    statement_md=(
        "设线性表 L = (a1, a2, …, an) 采用带头结点的单链表保存。"
        "请设计一个**空间复杂度为 O(1)** 且时间上尽可能高效的算法，重新排列各结点，"
        "得到 L′ = (a1, an, a2, an-1, a3, an-2, …)。\n\n"
        "为便于评测，输入输出用数组形式表示链表的内容。"
    ),
    input_md="第一行一个整数 n（1 ≤ n ≤ 3×10⁴）。\n第二行 n 个整数，表示链表 L 的元素值。",
    output_md="输出一行：重排后的元素序列，用单个空格分隔。",
    samples=[{"input": "5\n1 2 3 4 5\n", "output": "1 5 2 4 3\n"},
             {"input": "4\n1 2 3 4\n", "output": "1 4 2 3\n"},
             {"input": "1\n7\n", "output": "7\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct Node {\n    int data;\n    struct Node *next;\n} Node;\n\n"
        "/* TODO: 找中点 -> 逆置后半段 -> 交替归并 */\n"
        "int main(void){\n    int n;\n    scanf(\"%d\", &n);\n    return 0;\n}\n"),
    ref_c=S_2019_41_REF_C,
    gen=gen_2019_41, ref_py=ref_2019_41,
    solution_md=S_2019_41_SOLUTION,
)

# ============================================================
# 2020-41 三个升序数组的三元组最小距离
# ============================================================
def gen_2020_41(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n1, n2, n3 = rng.randint(1, 30), rng.randint(1, 30), rng.randint(1, 30)
        s1 = sorted(rng.sample(range(-100, 101), n1))
        s2 = sorted(rng.sample(range(-100, 101), n2))
        s3 = sorted(rng.sample(range(-100, 101), n3))
        n1, n2, n3 = len(s1), len(s2), len(s3)
        cases.append(f"{n1}\n{ints_line(s1)}{n2}\n{ints_line(s2)}{n3}\n{ints_line(s3)}")
    n1, n2, n3 = 15000, 17000, 19000
    s1 = sorted(rng.sample(range(-10**8, 10**8), n1))
    s2 = sorted(rng.sample(range(-10**8, 10**8), n2))
    s3 = sorted(rng.sample(range(-10**8, 10**8), n3))
    cases.append(f"{n1}\n{ints_line(s1)}{n2}\n{ints_line(s2)}{n3}\n{ints_line(s3)}")
    return cases


def ref_2020_41(case):
    toks = case.split()
    p = 0
    n1 = int(toks[p]); p += 1
    s1 = list(map(int, toks[p:p + n1])); p += n1
    n2 = int(toks[p]); p += 1
    s2 = list(map(int, toks[p:p + n2])); p += n2
    n3 = int(toks[p]); p += 1
    s3 = list(map(int, toks[p:p + n3]))
    i = j = k = 0
    best = None
    while i < n1 and j < n2 and k < n3:
        a, b, c = s1[i], s2[j], s3[k]
        d = 2 * (max(a, b, c) - min(a, b, c))
        if best is None or d < best:
            best = d
        m = min(a, b, c)
        if a == m:
            i += 1
        elif b == m:
            j += 1
        else:
            k += 1
    return f"{best}\n"


S_2020_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

static int read_arr(int **pa){
    int n; scanf("%d", &n);
    int *a = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    *pa = a;
    return n;
}

int main(void){
    int *A, *B, *C;
    int na = read_arr(&A), nb = read_arr(&B), nc = read_arr(&C);
    int i = 0, j = 0, k = 0;
    long best = -1;
    /* 三指针：D = 2*(max-min)，每次前移三者中"最小值"所在指针 */
    while (i < na && j < nb && k < nc){
        int a = A[i], b = B[j], c = C[k];
        int mx = a > b ? a : b; if (c > mx) mx = c;
        int mn = a < b ? a : b; if (c < mn) mn = c;
        long d = 2L * (mx - mn);
        if (best < 0 || d < best) best = d;
        if (mn == a) i++;
        else if (mn == b) j++;
        else k++;
    }
    printf("%ld\n", best);
    free(A); free(B); free(C);
    return 0;
}
"""

S_2020_41_SOLUTION = """## 考点

顺序表多指针（王道 2.2）。结论化简：**D = |a−b|+|b−c|+|c−a| = 2·(max−min)**，把三元组距离转成"最远两个数的距离"。

## 思路

三个数组升序。维护指针 i, j, k 和当前三元组 (A[i],B[j],C[k])：

1. 计算 D；
2. 把**最小值对应的指针**前移（前移它才可能让 max−min 变小；前移 max 或中间值都不可能改善）。

`min` 唯一时此步唯一，任意指针越界即结束（之后三数组取不齐，无意义）。

## 复杂度

时间 O(n1+n2+n3)，空间 O(1)。

## 考场提示

- 先证明 D = 2(max−min) 这一化简再写算法，设计思想一栏写清楚；
- 指针选择：移动**最小者**才有意义——这也是设计思想的答辩要点；
- 数据量大时读入、计算都要避免 O(n²) 枚举。
"""

P_2020_41 = dict(
    code="real-2020-41", title="三个升序数组的三元组最小距离", kind="exam", year=2020,
    exam_no="第41题", chapter="线性表", tags=["多指针", "归并思想"],
    difficulty=2, importance=5,
    statement_md=(
        "定义三元组 (a, b, c) 的距离 D = |a−b| + |b−c| + |c−a|。"
        "给定 3 个非空整数集合，按升序分别存储在 3 个数组中。\n\n"
        "请设计一个尽可能高效的算法，计算并输出所有可能的三元组中的**最小距离**。\n\n"
        "例如 S1={−1,0,9}，S2={−25,−10,10,11}，S3={2,9,17,30,41}，最小距离为 2。"
    ),
    input_md=(
        "输入依次给出三个数组：先一行整数 n1，再一行 n1 个升序整数；"
        "然后 n2 与其数组；最后 n3 与其数组（1 ≤ ni ≤ 2×10⁴）。"),
    output_md="输出一个整数：最小距离。",
    samples=[{"input": "3\n-1 0 9\n4\n-25 -10 10 11\n5\n2 9 17 30 41\n", "output": "2\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "/* 提示：D = 2*(max-min)，每次前移最小值所在的指针 */\n"
        "int main(void){\n    /* TODO */ \n    return 0;\n}\n"),
    ref_c=S_2020_41_REF_C,
    gen=gen_2020_41, ref_py=ref_2020_41,
    solution_md=S_2020_41_SOLUTION,
)

# ============================================================
# 2021-41 EL 路径判定
# ============================================================
def gen_2021_41(seed):
    rng = random.Random(seed)
    cases = []

    def connected_graph(n, m, mode):
        # 先建一棵生成树保证连通，再加随机边
        edges = set()
        perm = list(range(n))
        rng.shuffle(perm)
        for i in range(1, n):
            u, v = perm[i], perm[rng.randint(0, i - 1)]
            edges.add((min(u, v), max(u, v)))
        while len(edges) < m:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        return sorted(edges)

    # 欧拉（全偶度）：构造一个环
    def ring(n):
        return [(i, (i + 1) % n) for i in range(n)]

    cases.append("4 4\n0 1\n1 2\n2 3\n3 0\n")          # 环 -> 1
    cases.append("4 3\n0 1\n1 2\n2 3\n")                # 链 -> 1
    for _ in range(5):
        n = rng.randint(2, 12)
        m = rng.randint(n - 1, min(n * (n - 1) // 2, n + 12))
        edges = connected_graph(n, m, "rand")
        out = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(out) + "\n")
    for _ in range(2):
        n = rng.randint(5, 40)
        edges = ring(n) + []
        # 随机添边保持连通
        while rng.random() < 0.7:
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            e = (min(u, v), max(u, v))
            if u != v and e not in edges:
                edges.append(e)
        out = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(out) + "\n")
    return cases


def ref_2021_41(case):
    toks = case.split()
    p = 0
    n = int(toks[p]); m = int(toks[p + 1]); p += 2
    deg = [0] * n
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(toks[p]), int(toks[p + 1]); p += 2
        deg[u] += 1; deg[v] += 1
        adj[u].append(v); adj[v].append(u)
    odd = sum(1 for d in deg if d % 2 == 1)
    # 题设保证连通；仍校验一下（不完整数据稳妥）
    seen = [False] * n
    stack = [0]
    seen[0] = True
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if not seen[w]:
                seen[w] = True
                stack.append(w)
    if not all(seen):
        return "0\n"
    return ("1" if odd in (0, 2) else "0") + "\n"


S_2021_41_REF_C = r"""
#include <stdio.h>
#include <stdlib.h>

#define MAXV 105

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    static int edge[MAXV][MAXV];
    int deg[MAXV] = {0};
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        edge[u][v] = edge[v][u] = 1;
        deg[u]++; deg[v]++;
    }
    /* 奇度顶点计数 */
    int odd = 0;
    for (int i = 0; i < n; i++) if (deg[i] % 2) odd++;
    /* 连通性检查（DFS） */
    int vis[MAXV] = {0}, stack[MAXV], top = 0;
    stack[top++] = 0; vis[0] = 1;
    while (top){
        int u = stack[--top];
        for (int v = 0; v < n; v++)
            if (edge[u][v] && !vis[v]){ vis[v] = 1; stack[top++] = v; }
    }
    for (int i = 0; i < n; i++) if (!vis[i]){ printf("0\n"); return 0; }
    /* 0 个或 2 个奇度顶点 -> 存在 EL 路径 */
    printf("%d\n", (odd == 0 || odd == 2) ? 1 : 0);
    return 0;
}
"""

S_2021_41_SOLUTION = """## 考点

图的邻接矩阵 + 度的统计（王道 6 图）。此题把"一笔画"理论直接搬到 408 卷面：**无向连通图存在 EL 路径 ⟺ 奇度顶点数为 0 或 2**。

## 思路

1. 对每个顶点 i，邻接矩阵第 i 行 1 的个数即其度；奇度顶点个数记为 odd；
2. odd == 0 或 odd == 2 → 返回 1，否则返回 0；
3. 题目已保证 G 连通；如果不保证，需先 DFS/BFS 判断连通（骨架中保留这一检查，稳妥）。

## 复杂度

时间 O(n²)（邻接矩阵扫描），空间 O(n)。

## 考场提示

- "度为奇数的顶点个数为不大于 2 的偶数" ⇔ 0 或 2 个（奇度顶点个数恒为偶数，这条结论可以顺带写进设计思想）；
- 邻接矩阵下读出度：无向图行扫描即可；
- printf 返回值就是题目要求的 int。
"""

P_2021_41 = dict(
    code="real-2021-41", title="无向图的 EL 路径判定", kind="exam", year=2021,
    exam_no="第41题", chapter="图", tags=["邻接矩阵", "欧拉路径", "度"],
    difficulty=2, importance=5,
    statement_md=(
        "已知无向连通图 G，当 G 中度为奇数的顶点个数为不大于 2 的偶数时，"
        "G 存在包含所有边且长度为 |E| 的路径（称为 **EL 路径**）。\n\n"
        "设图 G 采用邻接矩阵存储。设计算法判断 G 是否存在 EL 路径，"
        "存在输出 1，否则输出 0。（输入保证边集非空；若图不连通也视为不存在。）"
    ),
    input_md=(
        "第一行两个整数 n（顶点数，顶点编号 0..n-1）和 m（边数）。\n"
        "之后 m 行，每行两个整数 u v 表示一条无向边（0 ≤ u < v < n）。"),
    output_md="输出 1 或 0。",
    samples=[{"input": "4 4\n0 1\n1 2\n2 3\n3 0\n", "output": "1\n"},
             {"input": "4 3\n0 1\n1 2\n2 3\n", "output": "1\n"},
             {"input": "4 3\n0 1\n0 2\n0 3\n", "output": "0\n"}],    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n\n#define MAXV 105\n\n"
        "int main(void){\n    int n, m;\n    scanf(\"%d %d\", &n, &m);\n"
        "    /* TODO: 读边建邻接矩阵，统计奇度顶点 */\n    return 0;\n}\n"),
    ref_c=S_2021_41_REF_C,
    gen=gen_2021_41, ref_py=ref_2021_41,
    solution_md=S_2021_41_SOLUTION,
)

PROBLEMS = [P_2017_41, P_2018_41, P_2019_41, P_2020_41, P_2021_41]
