"""Print the response-free M170 static evidence as JSON."""

from __future__ import annotations

import json

from m170_oriented_tensor_rank import static_results


if __name__ == "__main__":
    print(json.dumps(static_results(), indent=2, sort_keys=True))
