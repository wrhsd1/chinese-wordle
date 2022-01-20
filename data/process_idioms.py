"""
reviewed.txt 中，“屡试不爽”及以前的是直接从 THUOCL 的高频成语中筛选得到的；
之后的是根据高考成语，从 THUOCL 的成语中选出的。

correction.csv 中是在 THUOCL 中的成语，利用 pypinyin 和“新华词典”校对得到的。
对于不在 THUOCL 中的，“新华词典”注音错误的成语，直接扔掉。
"""

import json
from pathlib import Path

import pandas as pd
import pypinyin

HERE = Path(__file__).parent
ASSETS = HERE.parent / "src" / "assets"


def export_freq_idioms():
    review_df = pd.read_table(HERE / "reviewed.txt", header=None, names=["word"])
    xinhua_df = pd.read_json(HERE / "idiom.json")
    idiom_df = pd.merge(review_df, xinhua_df, on="word", how="inner")

    with open(ASSETS / "freq-idioms.json", "w") as f:
        json.dump(idiom_df["word"].tolist(), f, ensure_ascii=False)


def export_all_idioms():
    all_idioms = []
    output_idioms = {}

    pypinyin.load_single_dict({ord("子"): "zǐ,zi"})

    thu_df = pd.read_table(
        HERE / "THUOCL_chengyu.txt", header=None, sep="\s+", names=["word", "freq"]
    )
    correction_df = pd.read_csv(HERE / "correction.csv", index_col="word")

    with open(HERE / "idiom.json") as f:
        s = f.read().replace("　", " ").replace("ɡ", "g")
        all_idioms = json.loads(s)

    for idiom in all_idioms:
        if len(idiom["word"]) != 4:
            continue
        pinyin = " ".join(
            pypinyin.lazy_pinyin(
                idiom["word"],
                style=pypinyin.Style.TONE,
                v_to_u=True,
            )
        )
        if pinyin == idiom["pinyin"]:
            output_idioms[idiom["word"]] = idiom["pinyin"]
        else:
            if idiom["word"] in thu_df["word"].values:
                if idiom["word"] in correction_df.index:
                    output_idioms[idiom["word"]] = correction_df.loc[
                        idiom["word"]
                    ].pinyin
                else:
                    print(idiom["word"], idiom["pinyin"], pinyin, sep=",")

    with open(ASSETS / "all-idioms.json", "w") as f:
        json.dump(output_idioms, f, ensure_ascii=False)


if __name__ == "__main__":
    export_freq_idioms()
    export_all_idioms()