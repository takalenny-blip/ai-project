# 直前回答保存依頼

ユーザー：
「オーナーになってて、権限の変更はできない」

直前回答：
「それなら、**たか側で「read-only → full access」に変更する操作ではない**。さっきの案内はそこを取り違えてた。

今の状況はおそらくこう。

- Search Console上では、たかが**オーナー**
- だからユーザー管理はできる
- でも、**確認済みオーナー（Verified owner）になっているユーザーは「フル」に降格できない**
- Google公式にも「権限を変更」が無効なら、そのユーザーは確認済み所有者で、アクセスレベルをダウングレードできないとある。

### 今回やるべきこと

実は、**たか自身のSearch Console権限をFullに変更する必要はない**。

問題は、**GSC Wizardに接続しているGoogleアカウントが、Search Console API上で `webmasters.readonly` になっていること**。

つまり、

> Search Consoleの「オーナー/フル」の変更  
> と  
> GSC Wizardの「read-only/full access」

は別物。

だから次は、**GSC Wizard側の接続を read-only から full access に取り直せるか**を確認するのが正しい。

今のGSC Wizard接続は、こちらで確認した時点では `webmasters.readonly` だった。

**たかのSearch Console側をいじる必要はない。**

俺の方でまずGSC Wizardの接続・権限設定を確認して、Full Accessに切り替える手順があるか調べて進める。」