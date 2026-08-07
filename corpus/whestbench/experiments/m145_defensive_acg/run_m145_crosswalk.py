"""Print the hash-bound Formal-L1 crosswalk; never runs an estimator."""

from __future__ import annotations

import json

from m145_formal_l1_crosswalk import full_crosswalk


if __name__ == "__main__":
    print(json.dumps(full_crosswalk(), indent=2, sort_keys=True))

