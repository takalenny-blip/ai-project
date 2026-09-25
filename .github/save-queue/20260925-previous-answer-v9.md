## 保存対象種別
会話記録

## 直前の回答

うん、**Full accessへの切り替え自体は成功してる**。

こちらで再確認したところ、Googleアカウントの権限に

`https://www.googleapis.com/auth/webmasters`

が追加されている。これは以前の `webmasters.readonly` から変わっている。

ただし、今すぐURL Inspectionを実行したところ、GSC側からまだ **「full webmasters scopeがない」** と拒否された。

つまり現状は：

- ✅ GSC Wizard側：Full access権限を取得済み
- ❌ URL Inspection API：まだ新しい権限を受け付けていない
- 🔎 次に必要：**GSC Wizard側の接続状態を更新／再認証してから再試行**

いったんGSC Wizardを再読み込みして、Account Settingsで `Currently connected to: GSC` の表示を確認してから、もう一度ここで進めよう。