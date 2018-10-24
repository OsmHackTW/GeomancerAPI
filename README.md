# GeomancerAPI
鄉民風水師資料維護API

功能 | URI
---- | ----
用 GitHub OAuth2 登入 | /login/github
列出周遭的凶宅清單 | /unluckyhouse/list/{lat_min}/{lng_min}/{lat_max}/{lng_max}
新增凶宅 | /unluckyhouse/add
編輯凶宅 | /unluckyhouse/edit/{id}
凶宅資料上架 | /unluckyhouse/enable/{id}
凶宅資料下架 | /unluckyhouse/disable/{id}
