# zhihu-spider
知乎作者文章/专栏/答案 整理导出 pdf

## 已完成

- [] 下载知乎专栏文章导出 pdf
- [] 下载知乎作者所有文章导出 pdf

## todo

- [] 个人所有答案导出 pdf
- [] epub文件格式支持
- [] 使用 zhihu-oauth 重写 api
- [] 改进繁琐的 cookie 复制过程
- [] 使用 pyqt
- [] 代码逻辑分离

## 使用说明

### 运行环境

带有 `brew` 和 `python3` 的 `MacOS`

### 运行步骤

1. list.txt 中添加需要导出的专栏和个人文章页 url, 如下所示

```
https://zhuanlan.zhihu.com/c_72090295
https://www.zhihu.com/people/lfkdsk/posts
```

2. zhihu/config.json 中 cookie 字段需从浏览器复制

```json
{
    "cookie": "需要从浏览器复制",
}
```

3. 运行命令
```sh
# 只有第一次需要
sh ./install.sh

sh ./run.sh
```