import spacy
import json
import time
from nnsplit import NNSplit
import sys

sys.path.append("../train/")

from evaluate import SpacyInterface, NNSplitInterface  # noqa: E402


def time_batches(splitter_init, texts, n=5):
    times = []

    for _ in range(n):
        avg = 0

        for batch_size in [1, 4, 16, 64, 256, 1024]:
            print(splitter_init, batch_size)

            splitter = splitter_init(batch_size)

            start = time.time()
            splitter.split(texts)
            avg += time.time() - start

        times.append(avg / n)

    return times


if __name__ == "__main__":
    texts = json.load(open("sample.json", "r"))

    def spacy_sentencizer_init(bs):
        return SpacyInterface("de_core_news_sm", use_sentencizer=True, batch_size=bs)

    def spacy_tagger_init(bs):
        return SpacyInterface("de_core_news_sm", use_sentencizer=False, batch_size=bs)

    def nnsplit_init(**kwargs):
        return NNSplitInterface(NNSplit("../models/de/model.onnx", **kwargs))

    times = {}

    times["NNSplit (CPU)"] = time_batches(
        lambda bs: nnsplit_init(batch_size=bs, use_cuda=False), texts
    )
    times["NNSplit (GPU)"] = time_batches(
        lambda bs: nnsplit_init(batch_size=bs, use_cuda=True), texts
    )
    times["Spacy (Sentencizer)"] = time_batches(spacy_sentencizer_init, texts)

    times["Spacy (Tagger) (CPU)"] = time_batches(spacy_tagger_init, texts)
    spacy.require_gpu()
    times["Spacy (Tagger) (GPU)"] = time_batches(spacy_tagger_init, texts)

    print(times)