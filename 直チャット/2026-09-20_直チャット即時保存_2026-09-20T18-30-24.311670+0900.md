# 直チャット保存要求

## User
C:\Users\kiyam>find ~ -type f -name 'dimora-favorite-programs.json' 2>/dev/null
指定されたパスが見つかりません。

C:\Users\kiyam>find ~ -type f \( -iname '*dimora*' -o -iname '*favorite*program*' \) 2>/dev/null
指定されたパスが見つかりません。やり取り書き込んで。

## Bud
上記は Linux の `find` 構文を Windows のコマンドプロンプト（C:\Users\kiyam）で実行したものなので、この結果だけではJSONが存在しないとは判断できない。まず Windows 側で `where /r C:\ dimora-favorite-programs.json` を実行して探す。

## User
C:\Users\kiyam\Downloads\dimora-favorite-programs.json　やり取り書き込んで。
