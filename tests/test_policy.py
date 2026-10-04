# -*- coding: utf-8 -*-
"""408 源码合规检查测试。"""
from oj.policy import check_source, strip_comments_and_literals

OK_MAIN = r"""
#include <stdio.h>
#include <stdlib.h>
int main(){ int x; scanf("%d", &x); printf("%d\n", x+1); return 0; }
"""


def names(issues):
    return {(i.kind, i.name) for i in issues}


def test_ok_code_passes():
    assert check_source(OK_MAIN) == []


def test_banned_header_iostream():
    src = "#include <iostream>\nint main(){return 0;}"
    iss = check_source(src)
    assert ("header", "iostream") in names(iss)


def test_banned_header_windows():
    src = "#include <windows.h>\nint main(){return 0;}"
    assert any(i.name == "windows.h" for i in check_source(src))


def test_custom_path_header():
    src = '#include "foo/bar.h"\nint main(){return 0;}'
    assert any(i.kind == "header" for i in check_source(src))


def test_qsort_banned_in_standard():
    src = ("#include <stdio.h>\n#include <stdlib.h>\n"
           "int cmp(const void*a,const void*b){return 0;}\n"
           "int main(){int a[3]={1,2,3}; qsort(a,3,sizeof(int),cmp); return 0;}")
    assert ("identifier", "qsort") in names(check_source(src))


def test_fopen_banned():
    src = ('#include <stdio.h>\nint main(){ FILE *f = fopen("a.txt","r"); return 0;}')
    assert ("identifier", "fopen") in names(check_source(src))


def test_system_banned():
    src = '#include <stdlib.h>\nint main(){ system("dir"); return 0;}'
    assert ("identifier", "system") in names(check_source(src))


def test_gets_banned():
    src = '#include <stdio.h>\nint main(){ char s[10]; gets(s); return 0;}'
    assert ("identifier", "gets") in names(check_source(src))


def test_string_h_ok_standard():
    src = ('#include <stdio.h>\n#include <string.h>\n'
           'int main(){ char s[10]="ab"; printf("%d", (int)strlen(s)); return 0;}')
    assert check_source(src) == []


def test_strict_bans_string_h_and_strlen():
    src = ('#include <stdio.h>\n#include <string.h>\n'
           'int main(){ char s[10]="ab"; printf("%d", (int)strlen(s)); return 0;}')
    iss = check_source(src, {"level": "strict"})
    assert ("header", "string.h") in names(iss)
    assert ("identifier", "strlen") in names(iss)


def test_strict_allows_stdio_stdlib():
    assert check_source(OK_MAIN, {"level": "strict"}) == []


def test_comment_not_flagged():
    src = ('#include <stdio.h>\n// system("dir") 这里只是注释里的字\n'
           '/* #include <windows.h> 也是注释 */\n'
           'int main(){ char s[] = "fopen 字样"; printf("%s", s); return 0;}')
    assert check_source(src) == []


def test_strip_literals_keeps_line_numbers():
    src = 'int a; /* x\ny\nz */ int b;'
    out = strip_comments_and_literals(src)
    assert out.count("\n") == 2


def test_extra_allow():
    src = "#include <assert.h>\nint main(){return 0;}"
    assert check_source(src) != []
    assert check_source(src, {"extra_allow": ["assert.h"]}) == []


def test_line_numbers_reported():
    src = '#include <stdio.h>\n#include <windows.h>\nint main(){return 0;}'
    iss = check_source(src)
    assert iss[0].line == 2
    assert "第 2 行" in iss[0].fmt()
