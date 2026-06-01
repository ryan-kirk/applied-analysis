---
title: Home
comments: false
---

<section class="author-intro">
	<div class="author-profile">
		<img class="author-headshot" src="{{ '/assets/images/ryan-kirk-headshot-circle.png' | relative_url }}" alt="Ryan Kirk headshot">
		<div class="author-copy">
			<p class="home-kicker">About the author</p>
			<h2 class="home-title">Ryan Kirk</h2>
			<p class="home-summary">Ryan Kirk is a digital agriculture and applied AI leader focused on turning advanced technology into practical decision support. As former Head of Data Science at John Deere and a PhD in Human-Computer Interaction, he works at the intersection of analytics, product judgment, and real-world decision systems.</p>
		</div>
		<div class="author-qr-card">
			<img class="author-qr" src="{{ '/assets/images/ryan-kirk-qr.png' | relative_url }}" alt="QR code for Ryan Kirk contact link">
			<p class="author-qr-caption">Connect with Ryan</p>
		</div>
	</div>
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

This site extends the repository with a lightweight blog-style layer for shareable write-ups. Posts summarize individual examples, keep the interpretation public and educational, and use GitHub Discussions via giscus for comments. The source repository lives at <a href="https://github.com/ryan-kirk/applied-analysis">github.com/ryan-kirk/applied-analysis</a>.