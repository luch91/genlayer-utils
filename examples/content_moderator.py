# { "Depends": "py-genlayer:test" }
#
# Content Moderator — Example GenLayer Intelligent Contract
# Uses: nondet, llm, access_control helpers from genlayer-utils
#
# A contract that uses AI to classify user-submitted content as safe,
# spam, hate speech, or misinformation. Demonstrates role-based access
# and LLM classification templates.

import json
from dataclasses import dataclass
from genlayer import *


# ─── genlayer-utils: nondet ─────────────────────────────────────────────────

def llm_strict(prompt, *, response_format="json"):
    def _inner():
        result = gl.nondet.exec_prompt(prompt, response_format=response_format)
        if isinstance(result, dict):
            return json.dumps(result, sort_keys=True)
        return result
    raw = gl.eq_principle.strict_eq(_inner)
    if response_format == "json":
        return json.loads(raw)
    return raw


# ─── genlayer-utils: llm ────────────────────────────────────────────────────

def classify_prompt(text, categories, context=""):
    cats = "|".join(categories)
    ctx = f"\nCONTEXT: {context}\n" if context else ""
    return f"""Classify the following text into exactly one category.
{ctx}
TEXT: {text}

CATEGORIES: {cats}

Respond ONLY with this exact JSON format, nothing else:
{{"category": "<{cats}>", "confidence": "<high|medium|low>", "reason": "<1 sentence>"}}

Rules:
- Choose the single best-matching category
- Your response must be valid JSON only, no extra text"""


# ─── genlayer-utils: storage ────────────────────────────────────────────────

def increment_or_init(data, key, amount=1):
    current = data.get(key, 0)
    data[key] = current + amount


# ─── Contract ───────────────────────────────────────────────────────────────

CATEGORIES = ["safe", "spam", "hate_speech", "misinformation"]

@allow_storage
@dataclass
class Post:
    id: str
    content: str
    author: str
    category: str
    confidence: str
    reason: str
    is_moderated: bool


class ContentModerator(gl.Contract):
    posts: TreeMap[str, Post]
    post_count: u256
    flagged_count: TreeMap[str, u256]  # category -> count
    _roles: TreeMap[str, TreeMap[Address, bool]]

    def __init__(self):
        self.post_count = 0
        # Grant deployer admin role
        self._roles.get_or_insert_default("admin")[gl.message.sender_address] = True

    # ─── Role helpers ────────────────────────────────────────────────

    def _grant_role(self, role: str, account: Address) -> None:
        self._roles.get_or_insert_default(role)[account] = True

    def _has_role(self, role: str, account: Address) -> bool:
        role_map = self._roles.get_or_insert_default(role)
        return role_map.get(account, False)

    def _require_role(self, role: str) -> None:
        if not self._has_role(role, gl.message.sender_address):
            raise Exception(f"Missing required role: {role}")

    # ─── Public methods ──────────────────────────────────────────────

    @gl.public.write
    def submit_post(self, content: str) -> None:
        """Submit content for moderation."""
        self.post_count += 1
        post_id = f"post_{self.post_count}"

        self.posts[post_id] = Post(
            id=post_id,
            content=content,
            author=gl.message.sender_address.as_hex,
            category="pending",
            confidence="",
            reason="",
            is_moderated=False,
        )

    @gl.public.write
    def moderate(self, post_id: str) -> None:
        """Run AI classification on a post. Anyone can trigger moderation."""
        if post_id not in self.posts:
            raise Exception("Post not found")

        post = self.posts[post_id]
        if post.is_moderated:
            raise Exception("Post already moderated")

        # genlayer-utils: classify with one function call
        prompt = classify_prompt(
            text=post.content,
            categories=CATEGORIES,
            context="You are a content moderator for a decentralized platform.",
        )
        result = llm_strict(prompt)

        post.category = result["category"]
        post.confidence = result.get("confidence", "unknown")
        post.reason = result.get("reason", "")
        post.is_moderated = True

        # Track flagged content counts
        if post.category != "safe":
            increment_or_init(self.flagged_count, post.category)

    @gl.public.write
    def add_moderator(self, account: Address) -> None:
        """Grant moderator role (admin only)."""
        self._require_role("admin")
        self._grant_role("moderator", account)

    @gl.public.write
    def remove_post(self, post_id: str) -> None:
        """Remove a post (moderator or admin only)."""
        is_mod = self._has_role("moderator", gl.message.sender_address)
        is_admin = self._has_role("admin", gl.message.sender_address)
        if not (is_mod or is_admin):
            raise Exception("Only moderators or admins can remove posts")

        if post_id in self.posts:
            del self.posts[post_id]

    @gl.public.view
    def get_post(self, post_id: str) -> dict:
        if post_id not in self.posts:
            raise Exception("Post not found")
        p = self.posts[post_id]
        return {
            "id": p.id, "content": p.content, "author": p.author,
            "category": p.category, "confidence": p.confidence,
            "reason": p.reason, "is_moderated": p.is_moderated,
        }

    @gl.public.view
    def get_all_posts(self) -> list:
        return [
            {"id": p.id, "category": p.category, "is_moderated": p.is_moderated}
            for _, p in self.posts.items()
        ]

    @gl.public.view
    def get_stats(self) -> dict:
        stats = {}
        for cat, count in self.flagged_count.items():
            stats[cat] = count
        return stats
