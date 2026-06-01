---
title: Applied Analysis
comments: false
---

# Applied Analysis

Applied Analysis is a small public collection of practical analytical examples.

The goal is straightforward: take a real question, identify what is changing, extract a useful signal, and explain what it means in plain language.

## Latest Posts

{% if site.posts.size > 0 %}
{% for post in site.posts %}
### [{{ post.title }}]({{ post.url | relative_url }})

{{ post.date | date: "%B %-d, %Y" }}

{{ post.excerpt }}

{% endfor %}
{% else %}
No posts published yet.
{% endif %}

## About This Site

This site extends the repository with a lightweight blog-style layer for shareable write-ups. Posts summarize individual examples, keep the interpretation public and educational, and use GitHub Discussions via giscus for comments.