#!/usr/bin/python
import json


def _check():
    return [{"version": [], "stage": "check"}]


if __name__ == "__main__":
    print(json.dumps(_check()))
