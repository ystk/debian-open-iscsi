#!/bin/sh

# Upstream has always used Flex 2.5.35 to regenerate the lexer it
# shipped with open-iscsi so far. Howevever, 2.5.36 introduced a bug
# (upstream commit 9ba3187a) that broke POSIX compatibility, by
# changing the type of the global yyleng variable from int to size_t,
# breaking the explicit forward declaration in prom_parse.h. This bug
# was fixed in Flex 2.6.1 (upstream commit 7a7c3dfe), but some older
# Debian versions still carry a buggy Flex.
#
# The purpose of this script is to fix the generated output of flex
# to work around this bug for the time being.
#
# This workaround should probably be removed after the release of
# Stretch, because it's only relevant for backporting to Jessie.
#
# References:
# [9ba3187a] https://github.com/westes/flex/commit/9ba3187a537d6a58d345f2874d06087fd4050399
# [7a7c3dfe] https://github.com/westes/flex/commit/7a7c3dfe1bcb8230447ba1656f926b4b4cdfc457

exec perl -pe '
s/^extern yy_size_t yyleng/extern int yyleng/;
s/^yy_size_t yyleng/int yyleng/;
s/^yy_size_t yyget_leng/int yyget_leng/;
s/yyleng = \(size_t\)/yyleng = (int)/;
/^#define ECHO/ && s/yytext, yyleng/yytext, (size_t) yyleng/;
'
