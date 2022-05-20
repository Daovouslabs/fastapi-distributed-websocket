import re
from collections.abc import Generator


def _match_topic_with_wildcards(topic: str, pattern: str) -> bool:
    return (
        topic == pattern
        or '#' == pattern[:1]
        or pattern[:1] in (topic[:1], '+')
        and _match_topic_with_wildcards(
            topic[1:], pattern['+' != pattern[:1] or (topic[:1] in '/') * 2 :]
        )
    )


def matches(topic: str, patterns: list) -> bool:
    for pattern in patterns:
        if _match_topic_with_wildcards(topic, pattern):
            return True
    return False
    
