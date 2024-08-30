import re


def normalize_text(text):
    # 删除换行符和多余的空格，将所有空白字符替换为单一空格
    text = re.sub(r"\s+", " ", text).strip()

    # 替换标点符号
    text = re.sub(r"[。?？!！；;]", ".", text)  # 替换省略号、问号、感叹号、分号为句号
    text = re.sub(r"[？！]", ".", text)  # 替换英文问号、感叹号为句号
    text = re.sub(r"[：:]", ",", text)  # 替换冒号为逗号
    text = re.sub(r"[，,]", ",", text)  # 替换中文逗号为英文逗号

    # 删除特殊字符
    text = re.sub(r"[《》〈〉（）()“”‘’——¥]", "", text)  # 删除中文特殊字符
    text = re.sub(
        r"[<>\"\'\[\]\{\}\|\-\_\+\=\*\&\%\$\#\@\!\`]", "", text
    )  # 删除英文特殊字符

    # 将多个句号或逗号合并为一个
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r",{2,}", ",", text)
    text = re.sub(r"\.+", ".", text)

    return text
