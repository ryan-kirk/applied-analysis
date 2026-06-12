---
title: Blog
comments: false
---

This page collects the public case studies and analytical write-ups published from the Applied Analysis portfolio.

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
			<h2 class="post-card-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
			<p class="post-card-excerpt">{{ post.excerpt }}</p>
		</div>
	</article>
	{% endfor %}
	{% else %}
	<p>No case studies published yet.</p>
	{% endif %}
</section>
