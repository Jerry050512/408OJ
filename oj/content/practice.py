# -*- coding: utf-8 -*-
"""考点拆解练习题库：把 408 大题的子技能与选择题高频考点做成可评测小题。

重要度标注：
  ★5 大题直接相关、必须默写      ★4 大题子技能/选择题高频
  ★3 常规考点                    ★2 基础巩固
"""
from __future__ import annotations

import random


def ints(arr):
    return " ".join(str(x) for x in arr) + "\n"


# ============================ 顺序表 ============================

def gen_seq01(seed):
    rng = random.Random(seed)
    return [f"{n}\n{ints(rng.sample(range(-99, 100), n))}"
            for n in (1, 2, 5, 10, 30)]


def ref_seq01(case):
    t = case.split()
    n = int(t[0])
    a = [int(x) for x in t[1:1 + n]]
    mi = min(range(n), key=lambda i: a[i])
    a[mi] = a[-1]
    a.pop()
    return ints(a) if a else "\n"


C_SEQ01 = r"""
#include <stdio.h>

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int a[10005];
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 找最小值下标，用最后一个元素填补 */
    int mi = 0;
    for (int i = 1; i < n; i++) if (a[i] < a[mi]) mi = i;
    a[mi] = a[n - 1];
    n--;
    for (int i = 0; i < n; i++){
        if (i) putchar(' ');
        printf("%d", a[i]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_SEQ01 = """## 考点

顺序表原地删除（王道 2.2 例）。**用最后一个元素填洞**可以把删除代价从 O(n) 降到 O(1)，前提是不要求保留相对次序。

## 思路

一遍扫描找最小值下标 mi，`a[mi] = a[n-1]`，长度减一。

## 复杂度

时间 O(n)，空间 O(1)。

## 考场提示

注意 n=1 的边界：删除后表空。若不允许改变元素次序，则必须逐个前移（O(n)），别记混两种题型。
"""

P_SEQ01 = dict(
    code="prac-seq-01", title="顺序表删除最小值", kind="practice", chapter="线性表",
    tags=["顺序表", "删除"], difficulty=1, importance=3,
    statement_md=(
        "从顺序表中删除具有最小值的元素（假设唯一），并由**最后一个元素**填补空出的位置。"
        "输出删除后的顺序表。"),
    input_md="第一行整数 n（1 ≤ n ≤ 10⁴）。\n第二行 n 个互不相同的整数。",
    output_md="输出删除后的元素序列；表空则输出一个空行。",
    samples=[{"input": "5\n4 1 7 5 9\n", "output": "4 9 7 5\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SEQ01, gen=gen_seq01, ref_py=ref_seq01, solution_md=SOL_SEQ01,
)


def gen_seq02(seed):
    rng = random.Random(seed)
    return [f"{n}\n{ints([rng.randint(1, 99) for _ in range(n)])}"
            for n in (1, 2, 7, 16, 100)]


def ref_seq02(case):
    t = case.split()
    n = int(t[0])
    a = [int(x) for x in t[1:1 + n]]
    return ints(list(reversed(a)))


C_SEQ02 = r"""
#include <stdio.h>

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    int a[100005];
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 双指针对撞交换 */
    for (int i = 0, j = n - 1; i < j; i++, j--){
        int t = a[i]; a[i] = a[j]; a[j] = t;
    }
    for (int i = 0; i < n; i++){
        if (i) putchar(' ');
        printf("%d", a[i]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_SEQ02 = """## 考点

顺序表逆置（O(1) 空间），双指针基本功。它是 2019 链表重排、各类"原地操作"的基础动作。

## 思路

i 从头、j 从尾，交换后向中间收拢，直到 `i >= j`。

## 复杂度

时间 O(n)，空间 O(1)。
"""

P_SEQ02 = dict(
    code="prac-seq-02", title="顺序表就地逆置", kind="practice", chapter="线性表",
    tags=["顺序表", "双指针"], difficulty=1, importance=2,
    statement_md="设计空间复杂度为 O(1) 的算法，将顺序表 L 就地逆置，并输出逆置后的序列。",
    input_md="第一行整数 n（1 ≤ n ≤ 10⁵）。\n第二行 n 个整数。",
    output_md="输出逆置后的元素序列。",
    samples=[{"input": "5\n1 2 3 4 5\n", "output": "5 4 3 2 1\n"}],
    policy={"level": "strict"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SEQ02, gen=gen_seq02, ref_py=ref_seq02, solution_md=SOL_SEQ02,
)


def gen_seq03(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n, m = rng.randint(0, 15), rng.randint(0, 15)
        a = sorted(rng.randint(1, 60) for _ in range(n))
        b = sorted(rng.randint(1, 60) for _ in range(m))
        cases.append(f"{n} {m}\n{ints(a)}{ints(b)}")
    return cases


def ref_seq03(case):
    t = case.split()
    n, m = int(t[0]), int(t[1])
    a = [int(x) for x in t[2:2 + n]]
    b = [int(x) for x in t[2 + n:2 + n + m]]
    out = []
    i = j = 0
    while i < n and j < m:
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return ints(out) if out else "\n"


C_SEQ03 = r"""
#include <stdio.h>

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    int a[100005], b[100005];
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    for (int j = 0; j < m; j++) scanf("%d", &b[j]);
    /* 二路归并 */
    int i = 0, j = 0, first = 1;
    while (i < n && j < m){
        int v;
        if (a[i] <= b[j]) v = a[i++];
        else v = b[j++];
        if (!first) putchar(' ');
        printf("%d", v); first = 0;
    }
    while (i < n){ if (!first) putchar(' '); printf("%d", a[i++]); first = 0; }
    while (j < m){ if (!first) putchar(' '); printf("%d", b[j++]); first = 0; }
    putchar('\n');
    return 0;
}
"""

SOL_SEQ03 = """## 考点

二路归并（王道 2.2/7.5）。合并两个升序表是**归并排序**与 2012-41 真题的直接子技能。

## 思路

双指针各指一个表头，每次取较小者写入结果；一个表空后另一个表整体接上。

## 复杂度

时间 O(n+m)，空间 O(n+m)（输出）。最坏比较次数 n+m−1 —— 2012-41 的设计思想就靠它。

## 考场提示

取"较小者"时相等先取左表可保证归并排序是**稳定**的。
"""

P_SEQ03 = dict(
    code="prac-seq-03", title="合并两个升序顺序表", kind="practice", chapter="线性表",
    tags=["顺序表", "二路归并", "双指针"], difficulty=1, importance=4,
    statement_md="给定两个按升序排列的顺序表 A 与 B，请将它们合并为一个新的升序顺序表并输出。",
    input_md=(
        "第一行两个整数 n m，分别为两表长度（0 ≤ n, m ≤ 10⁵）。\n"
        "第二行 n 个升序整数（A）。\n第三行 m 个升序整数（B）。空表对应空行。"),
    output_md="输出合并后的升序序列（空格分隔）。",
    samples=[{"input": "3 4\n1 3 5\n2 4 6 8\n", "output": "1 2 3 4 5 6 8\n"},
             {"input": "0 2\n\n7 9\n", "output": "7 9\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SEQ03, gen=gen_seq03, ref_py=ref_seq03, solution_md=SOL_SEQ03,
)


# ============================ 链表 ============================

def gen_link01(seed):
    rng = random.Random(seed)
    return [f"{n}\n{ints([rng.randint(1, 99) for _ in range(n)])}"
            for n in (0, 1, 2, 6, 25)]


def ref_link01(case):
    t = case.split()
    n = int(t[0])
    a = [int(x) for x in t[1:1 + n]]
    return ints(list(reversed(a))) if a else "\n"


C_LINK01 = r"""
#include <stdio.h>
#include <stdlib.h>

typedef struct Node { int data; struct Node *next; } Node;

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    Node head; head.next = NULL;
    Node *tail = &head;
    for (int i = 0; i < n; i++){
        Node *p = (Node*)malloc(sizeof(Node));
        scanf("%d", &p->data); p->next = NULL;
        tail->next = p; tail = p;
    }
    /* 头插法就地逆置 */
    Node *prev = NULL, *cur = head.next;
    while (cur){
        Node *nx = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nx;
    }
    head.next = prev;
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

SOL_LINK01 = """## 考点

单链表就地逆置（王道 2.3），2019 年大题的第 2 步。考试推荐**三指针**写法，一行一图。

## 思路

prev / cur / next 三指针：保存后继 → 反转指针 → 三个一起前进。

替代写法是头插法（借助头结点逐个前插），同一思想。

## 复杂度

时间 O(n)，空间 O(1)。

## 考场提示

- 反转完成后与新链表头（prev）接好，旧头变成新尾，记得它的 next 已指向 NULL（由第一次迭代设置）；
- 空表和单结点直接通过。
"""

P_LINK01 = dict(
    code="prac-link-01", title="单链表就地逆置", kind="practice", chapter="线性表",
    tags=["单链表", "就地逆置"], difficulty=1, importance=4,
    statement_md=(
        "设计空间复杂度 O(1) 的算法，将带头结点的单链表就地逆置。"
        "评测输入输出以数组表示链表内容。"),
    input_md="第一行整数 n（0 ≤ n ≤ 10⁵）。\n第二行 n 个整数（n=0 时该行不存在）。",
    output_md="输出逆置后的元素序列。",
    samples=[{"input": "5\n1 2 3 4 5\n", "output": "5 4 3 2 1\n"},
             {"input": "0\n", "output": "\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct Node { int data; struct Node *next; } Node;\n\n"
        "int main(void){\n    /* TODO */\n    return 0;\n}\n"),
    ref_c=C_LINK01, gen=gen_link01, ref_py=ref_link01, solution_md=SOL_LINK01,
)


def gen_link02(seed):
    rng = random.Random(seed)
    return [f"{n}\n{ints([rng.randint(1, 99) for _ in range(n)])}"
            for n in (1, 2, 3, 8, 9, 40)]


def ref_link02(case):
    t = case.split()
    n = int(t[0])
    a = [int(x) for x in t[1:1 + n]]
    return f"{a[(n - 1) // 2]}\n"


C_LINK02 = r"""
#include <stdio.h>
#include <stdlib.h>

typedef struct Node { int data; struct Node *next; } Node;

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    Node head; head.next = NULL;
    Node *tail = &head;
    for (int i = 0; i < n; i++){
        Node *p = (Node*)malloc(sizeof(Node));
        scanf("%d", &p->data); p->next = NULL;
        tail->next = p; tail = p;
    }
    /* 快慢指针：快指针走两步，慢走一步 */
    Node *slow = head.next, *fast = head.next;
    while (fast && fast->next && fast->next->next){
        slow = slow->next;
        fast = fast->next->next;
    }
    printf("%d\n", slow->data);
    return 0;
}
"""

SOL_LINK02 = """## 考点

快慢指针（王道 2.3），2019 年大题第 1 步、找倒数第 k 个结点（2009 大题）的核心。

## 思路

不带头结点视角：快指针每次两步，慢指针每次一步。快指针走到尾部时慢指针即中点。
偶数个结点取**前半最后一个**（2019 重排需要的切分点）。

找倒数第 k 个：快指针先领先 k 步，再同步前进。

## 复杂度

时间 O(n)，空间 O(1)。
"""

P_LINK02 = dict(
    code="prac-link-02", title="找单链表的中间结点", kind="practice", chapter="线性表",
    tags=["单链表", "快慢指针"], difficulty=1, importance=4,
    statement_md=(
        "用一趟扫描找出单链表的中间结点：n 为奇数时取正中间（第 (n+1)/2 个，1-indexed），"
        "n 为偶数时取前半最后一个（第 n/2 个）。输出该结点值。"),
    input_md="第一行整数 n（1 ≤ n ≤ 10⁵）。\n第二行 n 个整数。",
    output_md="输出中间结点的值。",
    samples=[{"input": "5\n1 2 3 4 5\n", "output": "3\n"},
             {"input": "4\n1 2 3 4\n", "output": "2\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct Node { int data; struct Node *next; } Node;\n\n"
        "int main(void){\n    /* TODO */\n    return 0;\n}\n"),
    ref_c=C_LINK02, gen=gen_link02, ref_py=ref_link02, solution_md=SOL_LINK02,
)


def gen_link03(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n, m = rng.randint(0, 12), rng.randint(0, 12)
        a = sorted(rng.randint(1, 50) for _ in range(n))
        b = sorted(rng.randint(1, 50) for _ in range(m))
        cases.append(f"{n} {m}\n{ints(a)}{ints(b)}")
    return cases


def ref_link03(case):
    return ref_seq03(case)


C_LINK03 = r"""
#include <stdio.h>
#include <stdlib.h>

typedef struct Node { int data; struct Node *next; } Node;

static Node* build(int n){
    Node *head = (Node*)malloc(sizeof(Node));
    head->next = NULL;
    Node *tail = head;
    for (int i = 0; i < n; i++){
        Node *p = (Node*)malloc(sizeof(Node));
        scanf("%d", &p->data); p->next = NULL;
        tail->next = p; tail = p;
    }
    return head;
}

/* 合并两个带头结点的升序链表：直接重挂指针，不新建结点 */
static Node* merge(Node *A, Node *B){
    Node *h = (Node*)malloc(sizeof(Node));   /* 新链表的头结点 */
    Node *t = h;
    Node *pa = A->next, *pb = B->next;
    while (pa && pb){
        if (pa->data <= pb->data){ t->next = pa; pa = pa->next; }
        else { t->next = pb; pb = pb->next; }
        t = t->next;
    }
    t->next = pa ? pa : pb;
    free(A); free(B);
    return h;
}

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    Node *A = build(n), *B = build(m);
    Node *C = merge(A, B);
    int first = 1;
    for (Node *p = C->next; p; p = p->next){
        if (!first) putchar(' ');
        printf("%d", p->data);
        first = 0;
    }
    putchar('\n');
    return 0;
}
"""

SOL_LINK03 = """## 考点

单链表归并（王道 2.3）。指针版二路归并——2012-42、2019-41 的拼接动作都靠这个手感。

## 思路

借助一个局部头结点 C：pa/pb 较小者挂到 C 的尾部；剩下的表整段接上。
**只动指针不新建结点**，这才是链表题。

## 复杂度

时间 O(n+m)，空间 O(1)。

## 考场提示

- 相等先取 A 表，归并稳定；
- 尾部直接 `t->next = pa ? pa : pb`。
"""

P_LINK03 = dict(
    code="prac-link-03", title="合并两个升序链表", kind="practice", chapter="线性表",
    tags=["单链表", "二路归并"], difficulty=1, importance=4,
    statement_md=(
        "合并两个带头结点的升序单链表 A、B，要求结果仍升序，"
        "且**不新建数据结点**（只重挂指针）。评测输入输出以数组表示。"),
    input_md=(
        "第一行两个整数 n m。\n第二行 n 个升序整数；第三行 m 个升序整数（空表为空行）。"),
    output_md="输出合并后的升序序列。",
    samples=[{"input": "3 4\n1 3 5\n2 4 6 8\n", "output": "1 2 3 4 5 6 8\n"}],
    policy={"level": "standard"},
    lang_hint=(
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "typedef struct Node { int data; struct Node *next; } Node;\n\n"
        "int main(void){\n    /* TODO */\n    return 0;\n}\n"),
    ref_c=C_LINK03, gen=gen_link03, ref_py=ref_link03, solution_md=SOL_LINK03,
)


def gen_link04(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n, m = rng.randint(0, 12), rng.randint(0, 12)
        pool = rng.sample(range(1, 40), min(39, n + m + rng.randint(0, 5)))
        rng.shuffle(pool)
        a = sorted(pool[:n])
        b = sorted(rng.sample(range(1, 40), m))
        cases.append(f"{len(a)} {len(b)}\n{ints(a)}{ints(b)}")
    return cases


def ref_link04(case):
    t = case.split()
    n, m = int(t[0]), int(t[1])
    a = [int(x) for x in t[2:2 + n]]
    b = [int(x) for x in t[2 + n:2 + n + m]]
    i = j = 0
    out = []
    while i < n and j < m:
        if a[i] < b[j]:
            i += 1
        elif a[i] > b[j]:
            j += 1
        else:
            if not out or out[-1] != a[i]:
                out.append(a[i])
            i += 1; j += 1
    return ints(out) if out else "\n"


C_LINK04 = r"""
#include <stdio.h>

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    int a[100005], b[100005];
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    for (int j = 0; j < m; j++) scanf("%d", &b[j]);
    int i = 0, j = 0, first = 1, last = 0, started = 0;
    while (i < n && j < m){
        if (a[i] < b[j]) i++;
        else if (a[i] > b[j]) j++;
        else {
            if (!started || a[i] != last){
                if (!first) putchar(' ');
                printf("%d", a[i]);
                first = 0; last = a[i]; started = 1;
            }
            i++; j++;
        }
    }
    putchar('\n');
    return 0;
}
"""

SOL_LINK04 = """## 考点

两个升序表的交集（王道 2.2/2.3）。与归并共用"双指针谁小谁前进"的骨架， adds 去重输出。

## 思路

- a[i] < b[j] → i 前进；
- a[i] > b[j] → j 前进；
- 相等 → 记录并去重后两端一起前进。

## 复杂度

时间 O(n+m)，空间 O(1)。
"""

P_LINK04 = dict(
    code="prac-link-04", title="两个升序表的公共元素", kind="practice", chapter="线性表",
    tags=["双指针", "顺序表"], difficulty=1, importance=3,
    statement_md="给定两个升序数组 A、B，输出它们的公共元素（升序、去重）。",
    input_md="第一行 n m；第二行 A；第三行 B（空表为空行）。",
    output_md="输出公共元素序列；无公共元素输出空行。",
    samples=[{"input": "4 5\n1 2 3 6\n2 3 4 5 6\n", "output": "2 3 6\n"},
             {"input": "2 2\n1 2\n3 4\n", "output": "\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_LINK04, gen=gen_link04, ref_py=ref_link04, solution_md=SOL_LINK04,
)


# ============================ 栈 / 串 ============================

def gen_stack01(seed):
    rng = random.Random(seed)

    def good(depth):
        if depth == 0:
            return ""
        out = []
        for _ in range(rng.randint(0, 3)):
            pair = rng.choice(["()", "[]", "{}"])
            inner = good(depth - 1)
            out.append(pair[0] + inner + pair[1])
        rng.shuffle(out)
        return "".join(out)

    cases = [good(3) for _ in range(4)]
    bad = ["(]", "([)]", "((", "())(", "{[}]"]
    cases += bad
    return [s + "\n" for s in cases]


def ref_stack01(case):
    s = case.strip()
    pairs = {')': '(', ']': '[', '}': '{'}
    st = []
    for ch in s:
        if ch in "([{":
            st.append(ch)
        elif ch in ")]}":
            if not st or st[-1] != pairs[ch]:
                return "0\n"
            st.pop()
    return ("1" if not st else "0") + "\n"


C_STACK01 = r"""
#include <stdio.h>

char buf[100005];
char stk[100005];

int main(void){
    if (scanf("%100004s", buf) != 1){ printf("1\n"); return 0; }
    int top = 0, ok = 1;
    for (int i = 0; buf[i]; i++){
        char c = buf[i];
        if (c == '(' || c == '[' || c == '{') stk[top++] = c;
        else {
            char need = (c == ')') ? '(' : (c == ']') ? '[' : '{';
            if (top == 0 || stk[top - 1] != need){ ok = 0; break; }
            top--;
        }
    }
    if (top) ok = 0;
    printf("%d\n", ok);
    return 0;
}
"""

SOL_STACK01 = """## 考点

栈的经典应用（王道 3.3）。左括号入栈，右括号与栈顶配对。

## 思路

- 遇左括号入栈；
- 遇右括号：栈空或栈顶不配对 → 失配；否则弹栈；
- 结束栈必须为空。

## 复杂度

时间 O(n)，空间 O(n)。

## 考场提示

边界：空串视为匹配；题目可能扩展为"含其他字符"——忽略即可。
"""

P_STACK01 = dict(
    code="prac-stack-01", title="括号匹配", kind="practice", chapter="栈、队列与串",
    tags=["栈"], difficulty=1, importance=4,
    statement_md="给定仅含 `()[]{}` 三种括号的串，用栈判断括号是否匹配，匹配输出 1 否则输出 0。",
    input_md="一行括号串（长度 ≤ 10⁵，可能为空行）。",
    output_md="输出 1（匹配）或 0。",
    samples=[{"input": "([{}])\n", "output": "1\n"},
             {"input": "([)]\n", "output": "0\n"},
             {"input": "((\n", "output": "0\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_STACK01, gen=gen_stack01, ref_py=ref_stack01, solution_md=SOL_STACK01,
)


def gen_stack02(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        n = rng.randint(1, 9)
        perm = list(range(1, n + 1))
        rng.shuffle(perm)
        cases.append(f"{n}\n{' '.join(map(str, perm))}\n")
    return cases


def ref_stack02(case):
    t = case.split()
    n = int(t[0])
    out = [int(x) for x in t[1:1 + n]]
    st = []
    nxt = 1
    for x in out:
        while nxt <= x:
            st.append(nxt)
            nxt += 1
        if not st or st[-1] != x:
            return "0\n"
        st.pop()
    return "1\n"


C_STACK02 = r"""
#include <stdio.h>

int a[100005], stk[100005];

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 模拟入栈序列 1..n 验证出栈序列 */
    int top = 0, nxt = 1;
    for (int i = 0; i < n; i++){
        while (nxt <= a[i]) stk[top++] = nxt++;
        if (top == 0 || stk[top - 1] != a[i]){ printf("0\n"); return 0; }
        top--;
    }
    printf("1\n");
    return 0;
}
"""

SOL_STACK02 = """## 考点

出栈序列合法性（王道 3.1），**2026 年第 42 题直接考点**（与卡特兰数一起考的）。

## 思路

模拟：入栈顺序固定为 1..n。按给定出栈序列，每当需要的数还没入栈就继续入栈；栈顶正好是要出的数则弹出，否则非法。

## 复杂度

时间 O(n)，空间 O(n)。

## 考场提示

选择题常用的快速判据：出栈序列中任一元素 x，其**之后**比 x 小的元素必须递减排列（理由：x 出栈时已入栈的更小元素只能按入栈逆序弹出）。模拟法与判据都要会。n 个元素合法出栈序列总数 = 卡特兰数 C(2n,n)/(n+1)。
"""

P_STACK02 = dict(
    code="prac-stack-02", title="出栈序列合法性判定", kind="practice", chapter="栈、队列与串",
    tags=["栈", "出栈序列", "卡特兰数"], difficulty=2, importance=5,
    statement_md=(
        "入栈顺序固定为 1, 2, …, n。给定一个 1..n 的排列作为出栈序列，"
        "判断它是否为合法的出栈顺序，合法输出 1，否则输出 0。"),
    input_md="第一行整数 n（1 ≤ n ≤ 10⁵）。\n第二行为 1..n 的一个排列。",
    output_md="输出 1 或 0。",
    samples=[{"input": "5\n3 2 1 5 4\n", "output": "1\n"},
             {"input": "5\n3 4 1 5 2\n", "output": "0\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_STACK02, gen=gen_stack02, ref_py=ref_stack02, solution_md=SOL_STACK02,
)


def gen_stack03(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(2, 6)
        vals = [str(rng.randint(1, 20)) for _ in range(n)]
        ops = [rng.choice("+-*") for _ in range(n - 1)]  # 避免除法 C/Python 截断语义差异
        expr = vals[:]
        while len(expr) > 1:
            i = rng.randint(0, len(expr) - 2)
            op = ops.pop()
            expr[i:i + 2] = [f"({expr[i]} {op} {expr[i+1]})"]
        cases.append(expr[0])
    # 把中缀转后缀
    def to_rpn(s):
        prec = {'+': 1, '-': 1, '*': 2, '/': 2}
        out, st = [], []
        for tk in s.replace('(', ' ( ').replace(')', ' ) ').split():
            if tk.isdigit():
                out.append(tk)
            elif tk == '(':
                st.append(tk)
            elif tk == ')':
                while st[-1] != '(':
                    out.append(st.pop())
                st.pop()
            else:
                while st and st[-1] != '(' and prec[st[-1]] >= prec[tk]:
                    out.append(st.pop())
                st.append(tk)
        out.extend(reversed(st))
        return out
    return [" ".join(to_rpn(e)) + "\n" for e in cases]


def ref_stack03(case):
    toks = case.split()
    st = []
    for t in toks:
        if t == "+":
            b = st.pop(); a = st.pop(); st.append(a + b)
        elif t == "-":
            b = st.pop(); a = st.pop(); st.append(a - b)
        elif t == "*":
            b = st.pop(); a = st.pop(); st.append(a * b)
        elif t == "/":
            b = st.pop(); a = st.pop()
            q = abs(a) // abs(b)
            st.append(q if (a >= 0) == (b >= 0) else -q)  # C 截断到零
        else:
            st.append(int(t))
    return f"{st[-1]}\n"


C_STACK03 = r"""
#include <stdio.h>
#include <stdlib.h>

char tok[32];
long stk[100005];

int main(void){
    int top = 0;
    /* 操作数为非负整数；用首个字符区分操作符 */
    while (scanf("%31s", tok) == 1){
        char c = tok[0];
        if ((c == '+' || c == '-' || c == '*' || c == '/') && tok[1] == '\0'){
            long b = stk[--top], a = stk[--top];
            long r = 0;
            if (c == '+') r = a + b;
            else if (c == '-') r = a - b;
            else if (c == '*') r = a * b;
            else r = a / b;
            stk[top++] = r;
        } else {
            stk[top++] = atol(tok);
        }
    }
    printf("%ld\n", top > 0 ? stk[top - 1] : 0);
    return 0;
}
"""

SOL_STACK03 = """## 考点

栈求值（王道 3.3），选择题与潜在算法题双修：后缀（逆波兰）表达式求值。

## 思路

从左到右扫描：操作数入栈；遇操作符弹出两个操作数（**右操作数先弹**）计算后压回。

## 复杂度

时间 O(n)，空间 O(n)。

## 考场提示

- 减法和除法注意顺序：`-` 是 `先弹出的是右操作数`；
- 相关考点：中缀转后缀的栈表（`(` 入栈、`)` 弹到 `(`），常与 next 数组轮流出选择。
"""

P_STACK03 = dict(
    code="prac-stack-03", title="后缀表达式求值", kind="practice", chapter="栈、队列与串",
    tags=["栈", "表达式求值"], difficulty=1, importance=4,
    statement_md=(
        "给定一个后缀（逆波兰）表达式，操作数为非负整数，操作符含 `+ - * /`（除法整除），"
        "记号之间以空格分隔。求表达式的值。"),
    input_md="一行后缀表达式。",
    output_md="输出表达式的值。",
    samples=[{"input": "3 4 + 5 *\n", "output": "35\n"},
             {"input": "8 2 /\n", "output": "4\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n#include <stdlib.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_STACK03, gen=gen_stack03, ref_py=ref_stack03, solution_md=SOL_STACK03,
)


def gen_str01(seed):
    rng = random.Random(seed)
    pats = ["ababaaaba", "aaab", "abcabc", "aaaa", "xyzxyzxy", "abacabad"]
    cases = []
    for _ in range(6):
        m = rng.randint(2, 12)
        alpha = rng.choice(["ab", "abc"])
        cases.append("".join(rng.choice(alpha) for _ in range(m)) + "\n")
    for p in pats[:3]:
        cases.append(p + "\n")
    return cases


def ref_str01(case):
    p = case.strip()
    m = len(p)
    nxt = [0] * (m + 1)  # 1-indexed, 王道定义
    i, j = 1, 0
    while i < m:
        if j == 0 or p[i - 1] == p[j - 1]:
            i += 1
            j += 1
            nxt[i] = j
        else:
            j = nxt[j]
    return " ".join(str(nxt[k]) for k in range(1, m + 1)) + "\n"


C_STR01 = r"""
#include <stdio.h>

char p[100010];
int nxt[100010];

int main(void){
    if (scanf("%100000s", p + 1) != 1) return 0;   /* 1-indexed */
    int m = 0;
    while (p[m + 1]) m++;
    /* 王道定义 next：next[1]=0 */
    int i = 1, j = 0;
    while (i < m){
        if (j == 0 || p[i] == p[j]){ i++; j++; nxt[i] = j; }
        else j = nxt[j];
    }
    for (int k = 1; k <= m; k++){
        if (k > 1) putchar(' ');
        printf("%d", nxt[k]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_STR01 = """## 考点

KMP 的 next 数组（王道 4.2）。选择题**每年几乎必考**，务必能手推。

## 思路（王道定义，1-indexed）

`next[1] = 0`；`next[j]` = 模式串前 j−1 个字符中**最长相等前后缀长度** + 1。递推：

```
i=1, j=0
while i < m:
    if j==0 or p[i]==p[j]:  i++, j++, next[i]=j
    else:                    j = next[j]
```

## 复杂度

时间 O(m)，空间 O(m)。

## 考场提示

手推技巧：next[j] = p₁…p_{j−1} 的**最长相等前缀后缀**长度加 1；例 `ababaa` 的 next = 0 1 1 2 3 4。注意 408 旧教材也有 0 起始约定，答题以题目指定为准——本题用王道约定。
"""

P_STR01 = dict(
    code="prac-str-01", title="KMP 的 next 数组", kind="practice", chapter="栈、队列与串",
    tags=["串", "KMP"], difficulty=2, importance=5,
    statement_md=(
        "给定模式串 P（仅含小写字母），按王道教材约定计算其 next 数组（1-indexed）：\n"
        "`next[1] = 0`，`next[j]` 等于 P 前 j−1 个字符中最长相等前后缀的长度再加 1。"),
    input_md="一行模式串 P（2 ≤ |P| ≤ 10⁵）。",
    output_md="一行 m 个整数：next[1..m]，空格分隔。",
    samples=[{"input": "abaabc\n", "output": "0 1 1 2 2 3\n"},
             {"input": "ababaaaba\n", "output": "0 1 1 2 3 4 2 2 3\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_STR01, gen=gen_str01, ref_py=ref_str01, solution_md=SOL_STR01,
)


def gen_str02(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(8):
        m = rng.randint(1, 5)
        pat = "".join(rng.choice("ab") for _ in range(m))
        n = rng.randint(m, 40)
        txt = "".join(rng.choice("ab") for _ in range(n))
        cases.append(txt + "\n" + pat + "\n")
    return cases


def ref_str02(case):
    lines = case.split("\n")
    t, p = lines[0], lines[1].strip()
    idx = t.find(p)
    return f"{idx}\n"


C_STR02 = r"""
#include <stdio.h>

char t[100010], p[100010];
int nxt[100010];

int main(void){
    if (scanf("%100000s %100000s", t + 1, p + 1) != 2) return 0;
    int n = 0, m = 0;
    while (t[n + 1]) n++;
    while (p[m + 1]) m++;
    /* next 数组 */
    int i = 1, j = 0;
    while (i < m){
        if (j == 0 || p[i] == p[j]){ i++; j++; nxt[i] = j; }
        else j = nxt[j];
    }
    /* KMP 匹配 */
    i = 1; j = 1;
    while (i <= n && j <= m){
        if (j == 0 || t[i] == p[j]){ i++; j++; }
        else j = nxt[j];
    }
    if (j > m) printf("%d\n", i - m - 1);   /* 转为 0 起始下标 */
    else printf("-1\n");
    return 0;
}
"""

SOL_STR02 = """## 考点

KMP 匹配（王道 4.2）。

## 思路

求出 next 后做匹配：失配时 `j = next[j]`，主串指针 i 永不回退，故 O(n+m)。

## 复杂度

时间 O(n+m)，空间 O(m)。

## 考场提示

输出首次匹配位置（0 起始）；匹配完成时 `i - m` 就是 1-indexed 的位置，务必换算。
"""

P_STR02 = dict(
    code="prac-str-02", title="KMP 首次匹配位置", kind="practice", chapter="栈、队列与串",
    tags=["串", "KMP"], difficulty=2, importance=3,
    statement_md="用 KMP 算法在主串 T 中查找模式串 P 的首次出现位置（0 起始下标）。",
    input_md="第一行主串 T；第二行模式串 P（仅小写字母，|P| ≤ |T| ≤ 10⁵）。",
    output_md="输出首次匹配的下标；不存在输出 -1。",
    samples=[{"input": "ababcabcacbab\nabcac\n", "output": "5\n"},
             {"input": "ababc\nd\n", "output": "-1\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_STR02, gen=gen_str02, ref_py=ref_str02, solution_md=SOL_STR02,
)


# ============================ 树 ============================

def gen_tree01(seed):
    rng = random.Random(seed)
    cases = []
    for n in (1, 2, 5, 9, 30):
        vals = rng.sample(range(1, 500), n)

        def build(lst):
            if not lst:
                return None
            r = rng.randint(0, len(lst) - 1)
            return (build(lst[:r]), lst[r], build(lst[r + 1:]))

        t = build(vals)

        def pre(node):
            return [] if node is None else [node[1]] + pre(node[0]) + pre(node[2])

        p = pre(t)
        cases.append(f"{n}\n{ints(p)}{ints(vals)}")  # 该构造法的中序恰为 vals
    return cases


def ref_tree01(case):
    t = case.split()
    n = int(t[0])
    pre = [int(x) for x in t[1:1 + n]]
    ino = [int(x) for x in t[1 + n:1 + 2 * n]]
    pos = {v: i for i, v in enumerate(ino)}
    out = []

    def build(pl, pr, il, ir):
        if pl > pr:
            return
        r = pre[pl]
        k = pos[r]
        build(pl + 1, pl + k - il, il, k - 1)
        build(pl + k - il + 1, pr, k + 1, ir)
        out.append(r)

    build(0, n - 1, 0, n - 1)
    return ints(out)


C_TREE01 = r"""
#include <stdio.h>

int pre[5005], ino[5005], n;
int first = 1;

/* 先 preorder 后两边拼后序输出 */
static void build(int pl, int pr, int il, int ir){
    if (pl > pr) return;
    int r = pre[pl], k;
    for (k = il; ino[k] != r; k++);   /* 中序中找根 */
    build(pl + 1, pl + k - il, il, k - 1);
    build(pl + k - il + 1, pr, k + 1, ir);
    if (!first) putchar(' ');
    printf("%d", r);
    first = 0;
}

int main(void){
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &pre[i]);
    for (int i = 0; i < n; i++) scanf("%d", &ino[i]);
    build(0, n - 1, 0, n - 1);
    putchar('\n');
    return 0;
}
"""

SOL_TREE01 = """## 考点

由先序+中序重建二叉树（王道 5.3)，**几乎年年换个花样考**，大题与选择题都高频。

## 思路

- 先序第一个元素 = 根；
- 在中序里定位根 → 分出左右子树规模；
- 先输出左、再右、最后根（这就是把"重建"改成"直接打印后序"，不用真的建结点）。

## 复杂度

时间 O(n²)（中序定位用线性查找；可用下标数组降到 O(n)），空间 O(n)。

## 考场提示

- 后序中根**最后**输出，区分左右子树区间下标是常错点，建议画一遍区间；
- 前提：关键字互不相同；只有"先序+后序"**不能**唯一确定一棵树。
"""

P_TREE01 = dict(
    code="prac-tree-01", title="先序+中序求后序", kind="practice", chapter="树与二叉树",
    tags=["二叉树遍历", "重建"], difficulty=2, importance=5,
    statement_md=(
        "给定一棵二叉树的先序序列和中序序列（结点值互不相同），请输出它的后序序列。"),
    input_md="第一行 n（1 ≤ n ≤ 5×10³）。\n第二行先序序列。\n第三行中序序列。",
    output_md="输出后序序列（空格分隔）。",
    samples=[{"input": "5\n1 2 4 5 3\n2 4 5 1 3\n", "output": "5 4 2 3 1\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_TREE01, gen=gen_tree01, ref_py=ref_tree01, solution_md=SOL_TREE01,
)


def gen_tree_arr(seed):
    """生成层序数组表示的二叉树。"""
    rng = random.Random(seed)
    cases = []
    for n in (1, 3, 7, 15, 31):
        arr = ["-1"] * n
        arr[0] = str(rng.randint(1, 99))
        queue = [0]
        for i in queue:
            if 2 * i + 2 >= n:
                continue
            for c in (2 * i + 1, 2 * i + 2):
                if rng.random() < 0.8:
                    arr[c] = str(rng.randint(1, 99))
                    queue.append(c)
        cases.append(f"{n}\n{' '.join(arr)}\n")
    return cases


def gen_tree02(seed):
    return gen_tree_arr(seed)


def ref_height(case):
    t = case.split()
    n = int(t[0])
    a = t[1:1 + n]

    def h(i):
        if i >= n or a[i] == "-1":
            return 0
        return 1 + max(h(2 * i + 1), h(2 * i + 2))
    return f"{h(0)}\n"


C_TREE02 = r"""
#include <stdio.h>

int a[100005], n;

static int height(int i){
    if (i >= n || a[i] == -1) return 0;
    int l = height(2*i + 1), r = height(2*i + 2);
    return (l > r ? l : r) + 1;
}

int main(void){
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    printf("%d\n", height(0));
    return 0;
}
"""

SOL_TREE02 = """## 考点

二叉树高度的递归定义，王道 5.3 一切递归题的模板：
`height = 1 + max(height(左), height(右))`。

## 复杂度

时间 O(n)，空间 O(h)。
"""

P_TREE02 = dict(
    code="prac-tree-02", title="二叉树的高度", kind="practice", chapter="树与二叉树",
    tags=["二叉树", "递归"], difficulty=1, importance=4,
    statement_md=("给定层序数组表示的二叉树（-1 表示空），求树的高度（单结点树高度为 1，空树为 0）。"),
    input_md="第一行 n。\n第二行 n 个整数的层序序列。",
    output_md="输出树的高度。",
    samples=[{"input": "7\n1 2 3 4 5 -1 -1\n", "output": "3\n"},
             {"input": "1\n1\n", "output": "1\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_TREE02, gen=gen_tree02, ref_py=ref_height, solution_md=SOL_TREE02,
)


def gen_tree03(seed):
    return gen_tree_arr(seed + 999)


def ref_levelorder(case):
    t = case.split()
    n = int(t[0])
    a = t[1:1 + n]
    out = [x for x in a if x != "-1"]
    return " ".join(out) + "\n"


C_TREE03 = r"""
#include <stdio.h>

int a[100005], n;
int q[100005];

int main(void){
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 层序遍历：队列 */
    int head = 0, tail = 0, first = 1;
    if (a[0] != -1) q[tail++] = 0;
    while (head < tail){
        int i = q[head++];
        if (!first) putchar(' ');
        printf("%d", a[i]);
        first = 0;
        if (2*i + 1 < n && a[2*i + 1] != -1) q[tail++] = 2*i + 1;
        if (2*i + 2 < n && a[2*i + 2] != -1) q[tail++] = 2*i + 2;
    }
    putchar('\n');
    return 0;
}
"""

SOL_TREE03 = """## 考点

二叉树层序遍历（王道 5.3.2）：唯一必须借助**队列**完成的遍历方式。

## 思路

队列存结点下标；出队即访问；左、右孩子依次入队。
对顺序存储（堆式数组），层序就是跳过 -1 的原数组输出 —— 但代码必须用队列实现来练习。

## 复杂度

时间 O(n)，空间 O(n)。
"""

P_TREE03 = dict(
    code="prac-tree-03", title="二叉树层序遍历", kind="practice", chapter="树与二叉树",
    tags=["二叉树", "层序遍历", "队列"], difficulty=1, importance=4,
    statement_md="给定层序数组表示的二叉树（-1 表示空），用**队列**完成层序遍历并输出。",
    input_md="第一行 n。\n第二行层序序列。",
    output_md="输出层序遍历结果（空格分隔，不含空结点）。",
    samples=[{"input": "7\n1 2 3 -1 4 -1 5\n", "output": "1 2 3 4 5\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_TREE03, gen=gen_tree03, ref_py=ref_levelorder, solution_md=SOL_TREE03,
)


def gen_tree04(seed):
    rng = random.Random(seed)
    cases = []
    # 完全二叉树
    for n in (1, 6, 15, 31):
        arr = [str(rng.randint(1, 9)) for _ in range(n)]
        cases.append(f"{n}\n{' '.join(arr)}\n")
    # 非完全
    cases.append("7\n1 2 3 -1 4 -1 -1\n")
    cases.append("4\n1 2 -1 -1\n")
    cases.append("7\n1 2 3 -1 -1 -1 5\n")
    return cases


def ref_complete(case):
    t = case.split()
    n = int(t[0])
    a = t[1:1 + n]
    seen_null = False
    for i in range(n):
        if a[i] == "-1":
            seen_null = True
        elif seen_null:
            return "0\n"
    return "1\n"


C_TREE04 = r"""
#include <stdio.h>

int a[100005], n;

int main(void){
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 层序扫描：一旦遇到空结点，其后不应再有非空结点 */
    int seen_null = 0;
    for (int i = 0; i < n; i++){
        if (a[i] == -1) seen_null = 1;
        else if (seen_null){ printf("0\n"); return 0; }
    }
    printf("1\n");
    return 0;
}
"""

SOL_TREE04 = """## 考点

完全二叉树判定（王道 5.1），选择题经典。顺序存储下有个漂亮结论：

> 层序数组中第一个空结点之后，不允许再出现非空结点。

## 复杂度

时间 O(n)。
"""

P_TREE04 = dict(
    code="prac-tree-04", title="判定完全二叉树", kind="practice", chapter="树与二叉树",
    tags=["二叉树", "完全二叉树"], difficulty=2, importance=3,
    statement_md="给定层序数组表示的二叉树（-1 表示空，根必不为空），判定它是否为完全二叉树。",
    input_md="第一行 n。\n第二行层序序列。",
    output_md="输出 1（完全）或 0。",
    samples=[{"input": "7\n1 2 3 4 5 6 7\n", "output": "1\n"},
             {"input": "7\n1 2 3 -1 4 -1 -1\n", "output": "0\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_TREE04, gen=gen_tree04, ref_py=ref_complete, solution_md=SOL_TREE04,
)


def gen_bst01(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(6):
        n = rng.randint(1, 20)
        vals = rng.sample(range(1, 200), n)
        cases.append(f"{n}\n{ints(vals)}")
    return cases


def ref_bst01(case):
    t = case.split()
    n = int(t[0])
    vals = [int(x) for x in t[1:1 + n]]
    return ints(sorted(vals))


C_BST01 = r"""
#include <stdio.h>
#include <stdlib.h>

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
    return t;   /* 相等不插入 */
}

static int first = 1;
static void inorder(BSTNode *t){
    if (!t) return;
    inorder(t->left);
    if (!first) putchar(' ');
    printf("%d", t->data);
    first = 0;
    inorder(t->right);
}

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    BSTNode *root = NULL;
    for (int i = 0; i < n; i++){
        int v; scanf("%d", &v);
        root = insert(root, v);
    }
    inorder(root);
    putchar('\n');
    return 0;
}
"""

SOL_BST01 = """## 考点

BST 构造与中序遍历（王道 5.4）。结论：**BST 的中序序列 = 有序序列**——一切 BST 选择题的基石。

## 思路

按插入序列逐个插入（小于走左、大于走右、相等忽略），中序输出。

## 复杂度

时间平均 O(n log n)，最坏 O(n²)（升序/降序序列）；写考卷时记得提一句平衡树。
"""

P_BST01 = dict(
    code="prac-bst-01", title="BST 构造与中序遍历", kind="practice", chapter="树与二叉树",
    tags=["二叉搜索树", "中序遍历"], difficulty=1, importance=4,
    statement_md=(
        "给定 BST 的插入序列（关键字互不重复），按序列逐个插入构造 BST，输出中序遍历结果。"),
    input_md="第一行 n（1 ≤ n ≤ 10⁴）。\n第二行 n 个互不相同的整数。",
    output_md="输出中序序列（即升序序列）。",
    samples=[{"input": "5\n4 2 6 1 3\n", "output": "1 2 3 4 6\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n#include <stdlib.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_BST01, gen=gen_bst01, ref_py=ref_bst01, solution_md=SOL_BST01,
)


# ============================ 图 ============================

def gen_graph(seed, directed=False):
    rng = random.Random(seed)
    cases = []
    for n, m in ((1, 0), (2, 1), (4, 4), (6, 8), (10, 15)):
        edges = set()
        perm = list(range(n))
        rng.shuffle(perm)
        for i in range(1, n):
            u, v = perm[i], perm[rng.randint(0, i - 1)]
            edges.add((min(u, v), max(u, v)) if not directed else (u, v))
        while len(edges) < min(m, n * (n - 1) // 2):
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)) if not directed else (u, v))
        edges = sorted(edges)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_deg(case):
    t = case.split()
    p = 0
    n, m = int(t[p]), int(t[p + 1]); p += 2
    deg = [0] * n
    for _ in range(m):
        u, v = int(t[p]), int(t[p + 1]); p += 2
        deg[u] += 1; deg[v] += 1
    return ints(deg)


C_GRAPH01 = r"""
#include <stdio.h>

int deg[1005];

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        deg[u]++; deg[v]++;
    }
    for (int i = 0; i < n; i++){
        if (i) putchar(' ');
        printf("%d", deg[i]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_GRAPH01 = """## 考点

图的基本概念（王道 6.1）：顶点的度 = 邻接点数。这是 2021-41（奇度计数）、2023-41（出入度）的前置小题。

## 思路

读边时对两端顶点度各加 1（有向图则分别统计出度/入度）。

## 复杂度

时间 O(n+m)。
"""

P_GRAPH01 = dict(
    code="prac-graph-01", title="无向图各顶点的度", kind="practice", chapter="图",
    tags=["邻接矩阵", "度"], difficulty=1, importance=3,
    statement_md="给定无向图（顶点编号 0..n-1），输出每个顶点的度。",
    input_md="第一行 n m。\n之后 m 行，每行 u v 表示一条无向边。",
    output_md="一行 n 个整数：各顶点的度。",
    samples=[{"input": "4 3\n0 1\n1 2\n2 3\n", "output": "1 2 2 1\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_GRAPH01, gen=lambda seed: gen_graph(seed), ref_py=ref_deg, solution_md=SOL_GRAPH01,
)


def ref_dfs(case):
    t = case.split()
    p = 0
    n, m = int(t[p]), int(t[p + 1]); p += 2
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(t[p]), int(t[p + 1]); p += 2
        adj[u].append(v); adj[v].append(u)
    for a in adj:
        a.sort()
    vis = [False] * n
    out = []

    def dfs(u):
        vis[u] = True
        out.append(u)
        for w in adj[u]:
            if not vis[w]:
                dfs(w)
    dfs(0)
    return ints(out)


C_GRAPH02 = r"""
#include <stdio.h>

#define MAXV 1005

int adj[MAXV][MAXV], deg_[MAXV], vis[MAXV], n;
int first = 1;

static void dfs(int u){
    if (!first) putchar(' ');
    printf("%d", u);
    first = 0;
    vis[u] = 1;
    for (int i = 0; i < deg_[u]; i++)
        if (!vis[adj[u][i]]) dfs(adj[u][i]);
}

int main(void){
    int m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        adj[u][deg_[u]++] = v;
        adj[v][deg_[v]++] = u;
    }
    /* 邻接点按编号升序 */
    for (int u = 0; u < n; u++)
        for (int i = 0; i < deg_[u]; i++)
            for (int j = i + 1; j < deg_[u]; j++)
                if (adj[u][j] < adj[u][i]){
                    int t = adj[u][i]; adj[u][i] = adj[u][j]; adj[u][j] = t;
                }
    dfs(0);
    putchar('\n');
    return 0;
}
"""

SOL_GRAPH02 = """## 考点

深度优先遍历（王道 6.2）。**邻接点按编号升序**访问以保证序列唯一。

## 思路

`dfs(u)`：访问 → 标记 → 对未访问邻接点递归。邻接表存成数组数组并排序。

## 复杂度

时间 O(n+m)，空间 O(n)。

## 考场提示

- 顶点不连通时需要从每个未访问点重新开始；本题保证连通；
- DFS 序列往往是选择题"走迷宫"的模板。
"""

P_GRAPH02 = dict(
    code="prac-graph-02", title="无向图 DFS 序列", kind="practice", chapter="图",
    tags=["DFS", "邻接表"], difficulty=2, importance=4,
    statement_md=(
        "给定无向连通图（顶点编号 0..n-1），从顶点 0 出发做深度优先遍历，"
        "访问邻接点时**按编号升序**选择。输出 DFS 序列。"),
    input_md="第一行 n m。\n之后 m 行，每行 u v 表示无向边。图保证连通。",
    output_md="输出 DFS 访问序列（空格分隔）。",
    samples=[{"input": "4 4\n0 1\n1 2\n2 3\n3 0\n", "output": "0 1 2 3\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_GRAPH02, gen=lambda seed: gen_graph(seed), ref_py=ref_dfs, solution_md=SOL_GRAPH02,
)


def ref_bfs(case):
    t = case.split()
    p = 0
    n, m = int(t[p]), int(t[p + 1]); p += 2
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(t[p]), int(t[p + 1]); p += 2
        adj[u].append(v); adj[v].append(u)
    for a in adj:
        a.sort()
    vis = [False] * n
    out = []
    q = [0]
    vis[0] = True
    while q:
        u = q.pop(0)
        out.append(u)
        for w in adj[u]:
            if not vis[w]:
                vis[w] = True
                q.append(w)
    return ints(out)


C_GRAPH03 = r"""
#include <stdio.h>

#define MAXV 1005

int adj[MAXV][MAXV], deg_[MAXV], vis[MAXV], qu[MAXV*2], n;

int main(void){
    int m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        adj[u][deg_[u]++] = v;
        adj[v][deg_[v]++] = u;
    }
    for (int u = 0; u < n; u++)
        for (int i = 0; i < deg_[u]; i++)
            for (int j = i + 1; j < deg_[u]; j++)
                if (adj[u][j] < adj[u][i]){
                    int t = adj[u][i]; adj[u][i] = adj[u][j]; adj[u][j] = t;
                }
    /* BFS */
    int head = 0, tail = 0, first = 1;
    qu[tail++] = 0; vis[0] = 1;
    while (head < tail){
        int u = qu[head++];
        if (!first) putchar(' ');
        printf("%d", u);
        first = 0;
        for (int i = 0; i < deg_[u]; i++)
            if (!vis[adj[u][i]]){ vis[adj[u][i]] = 1; qu[tail++] = adj[u][i]; }
    }
    putchar('\n');
    return 0;
}
"""

SOL_GRAPH03 = """## 考点

广度优先遍历（王道 6.2），无权图最短路径的基础。用**队列**递层扩散。

## 思路

入队即标记（避免重复）；邻接点按编号升序压入。

## 复杂度

时间 O(n+m)，空间 O(n)。
"""

P_GRAPH03 = dict(
    code="prac-graph-03", title="无向图 BFS 序列", kind="practice", chapter="图",
    tags=["BFS", "队列"], difficulty=2, importance=4,
    statement_md=(
        "给定无向连通图，从顶点 0 出发做广度优先遍历，邻接点按编号升序访问。输出 BFS 序列。"),
    input_md="第一行 n m。\n之后 m 行，每行 u v。图保证连通。",
    output_md="输出 BFS 访问序列。",
    samples=[{"input": "4 4\n0 1\n1 2\n2 3\n3 0\n", "output": "0 1 3 2\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_GRAPH03, gen=lambda seed: gen_graph(seed), ref_py=ref_bfs, solution_md=SOL_GRAPH03,
)


def gen_graph04(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(7):
        n = rng.randint(1, 15)
        pairs = set()
        for _ in range(rng.randint(0, 20)):
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v:
                pairs.add((min(u, v), max(u, v)))
        edges = sorted(pairs)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_components(case):
    t = case.split()
    p = 0
    n, m = int(t[p]), int(t[p + 1]); p += 2
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for _ in range(m):
        u, v = int(t[p]), int(t[p + 1]); p += 2
        parent[find(u)] = find(v)
    return f"{len({find(i) for i in range(n)})}\n"


C_GRAPH04 = r"""
#include <stdio.h>

#define MAXV 1005

int par[MAXV];

static int find(int x){
    while (par[x] != x){ par[x] = par[par[x]]; x = par[x]; }
    return x;
}

int main(void){
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    for (int i = 0; i < n; i++) par[i] = i;
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        par[find(u)] = find(v);
    }
    int cnt = 0;
    for (int i = 0; i < n; i++) if (find(i) == i) cnt++;
    printf("%d\n", cnt);
    return 0;
}
"""

SOL_GRAPH04 = """## 考点

并查集 / 连通分量（王道 6 应用）。统计连通分量数也是判断欧拉回路连通性的子步骤。

## 思路

并查集：每条边合并两个集合；最后统计 root 个数。（也可用 DFS/BFS 计数。）

## 复杂度

时间 O((n+m)·α(n))。

## 考场提示

路径压缩的两行代码要背：`par[x] = par[par[x]]; x = par[x];`
"""

P_GRAPH04 = dict(
    code="prac-graph-04", title="连通分量计数", kind="practice", chapter="图",
    tags=["并查集", "连通性"], difficulty=2, importance=3,
    statement_md="给定无向图（顶点编号 0..n-1），统计它的连通分量个数。",
    input_md="第一行 n m。\n之后 m 行，每行 u v。",
    output_md="输出连通分量个数。",
    samples=[{"input": "5 2\n0 1\n2 3\n", "output": "3\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_GRAPH04, gen=gen_graph04, ref_py=ref_components, solution_md=SOL_GRAPH04,
)


def gen_graph05(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(7):
        n = rng.randint(1, 12)
        perm = list(range(n))
        rng.shuffle(perm)
        pos = {v: i for i, v in enumerate(perm)}
        edges = set()
        for _ in range(rng.randint(0, min(20, n * (n - 1) // 2))):
            u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if u != v and pos[u] < pos[v]:
                edges.add((u, v))
        edges = sorted(edges)
        lines = [f"{n} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
        cases.append("\n".join(lines) + "\n")
    return cases


def ref_topo_lex(case):
    t = case.split()
    p = 0
    n, m = int(t[p]), int(t[p + 1]); p += 2
    import heapq
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(t[p]), int(t[p + 1]); p += 2
        adj[u].append(v)
        indeg[v] += 1
    h = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(h)
    out = []
    while h:
        u = heapq.heappop(h)
        out.append(u)
        for w in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                heapq.heappush(h, w)
    return ints(out)


C_GRAPH05 = r"""
#include <stdio.h>

#define MAXV 1005

/* 小根堆取编号最小 */
int h[MAXV], hs;
static void push(int v){
    int i = hs++;
    h[i] = v;
    while (i > 0){
        int p = (i - 1) / 2;
        if (h[p] <= h[i]) break;
        int t = h[p]; h[p] = h[i]; h[i] = t; i = p;
    }
}
static int pop(void){
    int r = h[0];
    h[0] = h[--hs];
    int i = 0, x = h[0];
    for (;;){
        int l = 2*i+1, rr = 2*i+2, c;
        if (l >= hs) break;
        c = l;
        if (rr < hs && h[rr] < h[l]) c = rr;
        if (h[c] < x){ h[i] = h[c]; i = c; }
        else break;
    }
    h[i] = x;
    return r;
}

int adj[MAXV][MAXV], deg_[MAXV], indeg[MAXV], n;

int main(void){
    int m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    for (int i = 0; i < m; i++){
        int u, v; scanf("%d %d", &u, &v);
        adj[u][deg_[u]++] = v;
        indeg[v]++;
    }
    for (int i = 0; i < n; i++) if (indeg[i] == 0) push(i);
    int first = 1;
    while (hs){
        int u = pop();
        if (!first) putchar(' ');
        printf("%d", u);
        first = 0;
        for (int i = 0; i < deg_[u]; i++)
            if (--indeg[adj[u][i]] == 0) push(adj[u][i]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_GRAPH05 = """## 考点

拓扑排序（王道 6.4）+ 小根堆。当题目要求字典序最小的拓扑序列时，把 Kahn 算法里的队列换成**小根堆**。

## 思路

每轮从堆中弹出当前入度为 0 且编号最小的顶点；删边、更新入度、入堆。

## 复杂度

时间 O((n+m) log n)。

## 考场提示

2024-41 唯一拓扑判定的姊妹题：若每轮堆里恰有一个元素，则序列唯一。
"""

P_GRAPH05 = dict(
    code="prac-graph-05", title="字典序最小拓扑序列", kind="practice", chapter="图",
    tags=["拓扑排序", "堆"], difficulty=2, importance=4,
    statement_md=("给定有向无环图，输出**字典序最小**（每轮取编号最小）的拓扑序列。"),
    input_md="第一行 n m。\n之后 m 行每行 u v 表示有向边 u→v。",
    output_md="输出拓扑序列。",
    samples=[{"input": "4 3\n0 1\n0 2\n1 3\n", "output": "0 1 2 3\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_GRAPH05, gen=gen_graph05, ref_py=ref_topo_lex, solution_md=SOL_GRAPH05,
)


# ============================ 排序 / 查找 ============================

def gen_sort01(seed):
    rng = random.Random(seed)
    return [f"{n}\n{ints([rng.randint(1, 60) for _ in range(n)])}"
            for n in (2, 5, 9, 20, 50)]


def partition_wd(a):
    """王道/Lomuto 式一次划分：pivot=首元素，双指针对撞。"""
    low, high = 0, len(a) - 1
    pivot = a[low]
    while low < high:
        while low < high and a[high] >= pivot:
            high -= 1
        a[low] = a[high]
        while low < high and a[low] <= pivot:
            low += 1
        a[high] = a[low]
    a[low] = pivot
    return low


def ref_sort01(case):
    t = case.split()
    n = int(t[0])
    a = [int(x) for x in t[1:1 + n]]
    p = partition_wd(a)
    return ints(a) + f"{p}\n"


C_SORT01 = r"""
#include <stdio.h>

int a[100005];

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 王道 QuickSort 一次划分：pivot = 首元素 */
    int low = 0, high = n - 1, pivot = a[0];
    while (low < high){
        while (low < high && a[high] >= pivot) --high;
        a[low] = a[high];
        while (low < high && a[low] <= pivot) ++low;
        a[high] = a[low];
    }
    a[low] = pivot;
    for (int i = 0; i < n; i++){
        if (i) putchar(' ');
        printf("%d", a[i]);
    }
    printf("\n%d\n", low);
    return 0;
}
"""

SOL_SORT01 = """## 考点

快速排序的**一次划分**（王道 7.3），选择题年年送命题，代码本身也是排序题地基。

## 思路

pivot = 首元素；high 从右往左找 `< pivot` 填到低位坑，low 从左往右找 `> pivot` 填到高位坑；两指针相遇把 pivot 放进坑。

## 复杂度

时间 O(n)，空间 O(1)。

## 考场提示

- 填空动作 4 行循环体顺序：先高端后低端；
- 相等时移动方向（`>=` / `<=`）要保持与王道一致，别写成死循环；
- 该过程是 2016-43 等题"手写快排"的核心。
"""

P_SORT01 = dict(
    code="prac-sort-01", title="快速排序的一次划分", kind="practice", chapter="排序",
    tags=["快速排序", "双指针"], difficulty=2, importance=5,
    statement_md=(
        "对给定数组执行快速排序的**一次划分**（取首元素为枢轴，王道教材的双指针对撞过程）。\n"
        "输出划分后的数组与枢轴的最终下标。"),
    input_md="第一行 n（2 ≤ n ≤ 10⁴）。\n第二行 n 个整数。",
    output_md="第一行输出划分后的数组。\n第二行输出枢轴最终下标（0 起始）。",
    samples=[{"input": "5\n3 1 4 1 5\n", "output": "1 1 3 4 5\n2\n"}],
    policy={"level": "strict"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SORT01, gen=gen_sort01, ref_py=ref_sort01, solution_md=SOL_SORT01,
)


def gen_sort02(seed):
    rng = random.Random(seed)
    return [f"{n}\n{ints([rng.randint(1, 99) for _ in range(n)])}"
            for n in (1, 4, 7, 12, 30)]


def ref_sort02(case):
    t = case.split()
    n = int(t[0])
    vals = [int(x) for x in t[1:1 + n]]
    heap = []

    def up(i):
        while i > 0:
            p = (i - 1) // 2
            if heap[p] >= heap[i]:
                break
            heap[p], heap[i] = heap[i], heap[p]
            i = p
    for v in vals:
        heap.append(v)
        up(len(heap) - 1)
    return ints(heap)


C_SORT02 = r"""
#include <stdio.h>

int h[100005], hs;

static void push(int v){
    int i = hs++;
    h[i] = v;
    while (i > 0){
        int p = (i - 1) / 2;
        if (h[p] >= h[i]) break;
        int t = h[p]; h[p] = h[i]; h[i] = t; i = p;
    }
}

int main(void){
    int n;
    if (scanf("%d", &n) != 1) return 0;
    for (int i = 0; i < n; i++){
        int v; scanf("%d", &v);
        push(v);
    }
    for (int i = 0; i < hs; i++){
        if (i) putchar(' ');
        printf("%d", h[i]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_SORT02 = """## 考点

堆的插入（王道 7.4）：新元素放在末尾，**上浮**到合适位置。2022-42（堆）与 2024-41 的子技能。

## 思路

`sift_up`：与父结点比较，大者上浮。堆序只保证父 ≥ 子，不保证同层有序。

## 复杂度

单次插入 O(log n)。

## 考场提示

与"建堆"（自底向上 sift_down，O(n)）区分：插入 n 个元素是 O(n log n)。
"""

P_SORT02 = dict(
    code="prac-sort-02", title="大根堆逐个插入", kind="practice", chapter="排序",
    tags=["堆", "大根堆"], difficulty=1, importance=4,
    statement_md="向空的大根堆中逐个插入给定序列，输出最终的堆数组。",
    input_md="第一行 n（1 ≤ n ≤ 10⁴）。\n第二行 n 个整数。",
    output_md="输出最终大根堆的数组形式。",
    samples=[{"input": "5\n3 1 4 1 5\n", "output": "5 4 3 1 1\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SORT02, gen=gen_sort02, ref_py=ref_sort02, solution_md=SOL_SORT02,
)


def gen_sort03(seed):
    rng = random.Random(seed)
    out = []
    for _ in range(6):
        n = rng.randint(2, 30)
        size = rng.randint(1, 7)
        arr = [rng.randint(1, 99) for _ in range(n)]
        # 保证每个 k 段有序（归并排序进行中状态）
        for i in range(0, n, size):
            arr[i:i + size] = sorted(arr[i:i + size])
        out.append(f"{n} {size}\n{ints(arr)}")
    return out


def ref_sort03(case):
    t = case.split()
    n, k = int(t[0]), int(t[1])
    a = [int(x) for x in t[2:2 + n]]
    res = []
    i = 0
    while i < n:
        j = min(i + k, n)
        lo = min(i + 2 * k, n)
        # 归并 a[i:j], a[j:lo]
        left, right = a[i:j], a[j:lo]
        m = []
        x = y = 0
        while x < len(left) and y < len(right):
            if left[x] <= right[y]:
                m.append(left[x]); x += 1
            else:
                m.append(right[y]); y += 1
        m += left[x:] + right[y:]
        res += m
        i += 2 * k
    return ints(res)


C_SORT03 = r"""
#include <stdio.h>

int a[100005], tmp[100005];

int main(void){
    int n, k;
    if (scanf("%d %d", &n, &k) != 2) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    /* 一趟二路归并：段长 k */
    for (int lo = 0; lo < n; lo += 2 * k){
        int mid = lo + k; if (mid > n) mid = n;
        int hi = lo + 2 * k; if (hi > n) hi = n;
        int i = lo, j = mid, t = lo;
        while (i < mid && j < hi){
            if (a[i] <= a[j]) tmp[t++] = a[i++];
            else tmp[t++] = a[j++];
        }
        while (i < mid) tmp[t++] = a[i++];
        while (j < hi) tmp[t++] = a[j++];
        for (t = lo; t < hi; t++) a[t] = tmp[t];
    }
    for (int i = 0; i < n; i++){
        if (i) putchar(' ');
        printf("%d", a[i]);
    }
    putchar('\n');
    return 0;
}
"""

SOL_SORT03 = """## 考点

归并排序的**一趟**（王道 7.5）：把数组按段长 k 两两归并。

## 思路

外层以 2k 为步长扫数组，内部做标准的二路归并同时写回原数组。

## 复杂度

时间 O(n)，辅助空间 O(n)。

## 考场提示

写归并时的指针模板：`i = lo, j = mid, t = lo`，比较方向 `<=` 取左保持稳定性。
"""

P_SORT03 = dict(
    code="prac-sort-03", title="归并排序的一趟", kind="practice", chapter="排序",
    tags=["归并排序"], difficulty=2, importance=3,
    statement_md=(
        "给定数组与段长 k，执行**一趟**二路归并（相邻两段合并且写回），输出归并后的数组。"),
    input_md="第一行 n 与 k（1 ≤ k ≤ n ≤ 10⁵）。\n第二行 n 个整数。",
    output_md="输出一趟归并后的数组。",
    samples=[{"input": "6 2\n1 5 3 4 2 6\n", "output": "1 3 4 5 2 6\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SORT03, gen=gen_sort03, ref_py=ref_sort03, solution_md=SOL_SORT03,
)


def gen_search01(seed):
    rng = random.Random(seed)
    cases = []
    for _ in range(7):
        n = rng.randint(1, 30)
        a = rng.sample(range(1, 200), n)
        a.sort()
        t = rng.choice(a + [x for x in range(1, 210) if x not in a][:10])
        cases.append(f"{n} {t}\n{ints(a)}")
    return cases


def ref_search01(case):
    t = case.split()
    n, key = int(t[0]), int(t[1])
    a = [int(x) for x in t[2:2 + n]]
    lo, hi = 0, n - 1
    cnt = 0
    pos = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        cnt += 1
        if a[mid] == key:
            pos = mid
            break
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    if pos >= 0:
        return f"{pos} {cnt}\n"
    return f"-1 {cnt}\n"


C_SEARCH01 = r"""
#include <stdio.h>

int a[100005];

int main(void){
    int n, key;
    if (scanf("%d %d", &n, &key) != 2) return 0;
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    int lo = 0, hi = n - 1, cnt = 0, pos = -1;
    while (lo <= hi){
        int mid = (lo + hi) / 2;
        cnt++;
        if (a[mid] == key){ pos = mid; break; }
        else if (a[mid] < key) lo = mid + 1;
        else hi = mid - 1;
    }
    printf("%d %d\n", pos, cnt);
    return 0;
}
"""

SOL_SEARCH01 = """## 考点

二分查找（王道 7.2），需要记住"比较次数"的统计方法（与平均查找长度 ASL 挂钩）。

## 复杂度

时间 O(log n)。

## 考场提示

`mid = (lo + hi) / 2` 向下取整；循环不变量 `lo <= hi`；输出未命中时的比较次数也别漏写。
"""

P_SEARCH01 = dict(
    code="prac-search-01", title="二分查找及比较次数", kind="practice", chapter="查找",
    tags=["二分查找"], difficulty=1, importance=4,
    statement_md=(
        "给定升序数组与关键字，执行二分查找，"
        "输出查找位置（0 起始，找不到输出 -1）与所用的**比较次数**。"),
    input_md="第一行 n 与 key。\n第二行 n 个升序整数。",
    output_md="输出两个整数：位置 比较次数。",
    samples=[{"input": "5 4\n1 2 4 7 9\n", "output": "2 1\n"},
             {"input": "5 5\n1 2 4 7 9\n", "output": "-1 2\n"}],
    policy={"level": "standard"},
    lang_hint="#include <stdio.h>\n\nint main(void){\n    /* TODO */\n    return 0;\n}\n",
    ref_c=C_SEARCH01, gen=gen_search01, ref_py=ref_search01, solution_md=SOL_SEARCH01,
)


# ============================================================

PROBLEMS = [
    P_SEQ01, P_SEQ02, P_SEQ03,
    P_LINK01, P_LINK02, P_LINK03, P_LINK04,
    P_STACK01, P_STACK02, P_STACK03,
    P_STR01, P_STR02,
    P_TREE01, P_TREE02, P_TREE03, P_TREE04,
    P_BST01,
    P_GRAPH01, P_GRAPH02, P_GRAPH03, P_GRAPH04, P_GRAPH05,
    P_SORT01, P_SORT02, P_SORT03,
    P_SEARCH01,
]
