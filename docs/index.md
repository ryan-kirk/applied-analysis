---
title: Home
comments: false
---

<section class="home-intro">
	<p class="home-kicker">Signal-first analysis</p>
	<h2 class="home-title">Small public write-ups that turn data into something easier to notice and explain.</h2>
	<p class="home-summary">Applied Analysis is a small public collection of practical analytical examples. Each post starts with a real question, looks for the signal that matters, and explains the result in plain language.</p>
</section>

## Latest Posts

<section class="post-list">
	{% if site.posts.size > 0 %}
	{% for post in site.posts %}
	<article class="post-card">
		{% if post.image %}
		<a class="post-card-image-link" href="{{ post.url | relative_url }}">
			<img class="post-card-image" src="{{ post.image | relative_url }}" alt="{{ post.image_alt | default: post.title }}">
		</a>
		{% endif %}
		<div class="post-card-body">
			<p class="post-card-date">{{ post.date | date: "%B %-d, %Y" }}</p>
			<h3 class="post-card-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
			<p class="post-card-excerpt">{{ post.excerpt }}</p>
		</div>
	</article>
	{% endfor %}
	{% else %}
	<p>No posts published yet.</p>
	{% endif %}
</section>

## About This Site

This site extends the repository with a lightweight blog-style layer for shareable write-ups. Posts summarize individual examples, keep the interpretation public and educational, and use GitHub Discussions via giscus for comments.