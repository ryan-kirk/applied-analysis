---
title: Home
comments: false
---

<section class="home-positioning">
	<p class="home-positioning-kicker">Applied AI, analytics, and decision support</p>
	<h2 class="home-positioning-title">A working portfolio of analytical systems, public case studies, and practical software.</h2>
	<p class="home-positioning-copy">This site highlights how Ryan Kirk approaches real-world problems: define the decision, extract the signal, make the system legible, and turn technical work into something decision-makers can actually use.</p>
</section>

<section class="author-intro">
	<div class="author-profile">
		<img class="author-headshot" src="{{ '/assets/images/ryan-kirk-headshot-circle.png' | relative_url }}" alt="Ryan Kirk headshot">
		<div class="author-copy">
			<p class="home-kicker">About the author</p>
			<h2 class="home-title">Ryan Kirk</h2>
			<p class="home-summary">Ryan Kirk works at the intersection of applied AI, analytics, product judgment, and operational decision support. As former Head of Data Science at John Deere and a PhD in Human-Computer Interaction, he focuses on turning complex technical systems into clear tools, signals, and workflows that help organizations decide with more confidence.</p>
		</div>
		<div class="author-qr-card">
			<img class="author-qr" src="{{ '/assets/images/ryan-kirk-qr.png' | relative_url }}" alt="QR code for Ryan Kirk contact link">
			<p class="author-qr-caption">Connect with Ryan</p>
		</div>
	</div>
</section>

## Selected Projects

<p class="section-intro">Selected applications across analytics, decision support, geospatial exploration, research tooling, and workflow design.</p>

<section class="project-list">
	{% assign projects = site.projects | sort: 'order' %}
	{% for project in projects %}
	<article class="project-card">
		<a class="project-card-media" href="{{ project.url | relative_url }}">
			{% if project.image %}
			<img class="project-card-image" src="{{ project.image | relative_url }}" alt="{{ project.image_alt | default: project.title }}">
			{% else %}
			<div class="project-card-placeholder" role="img" aria-label="Placeholder thumbnail for {{ project.title }}">
				<p class="project-card-placeholder-kicker">{{ project.category_label | default: 'Application' }}</p>
				<h3 class="project-card-placeholder-title">Preview Coming Soon</h3>
				<p class="project-card-placeholder-note">{{ project.title }}</p>
			</div>
			{% endif %}
		</a>
		<p class="project-card-kicker">{{ project.category_label | default: 'Project' }}</p>
		<p class="project-card-meta">{{ project.access_label | default: 'Public repository' }}</p>
		<h3 class="project-card-title"><a href="{{ project.url | relative_url }}">{{ project.title }}</a></h3>
		<p class="project-card-summary">{{ project.summary }}</p>
		<p class="project-card-links">
			<a href="{{ project.url | relative_url }}">Project profile</a>
			{% if project.repo_visibility == 'public' and project.repo_url %}<a href="{{ project.repo_url }}">Repository</a>{% endif %}
		</p>
	</article>
	{% endfor %}
</section>

## Recent Case Studies

<p class="section-intro">Public write-ups drawn from the Applied Analysis work. They remain available as examples, but the main purpose of the site is to show the thinking, framing, and implementation behind the work.</p>

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

This site functions as a portfolio layer on top of the repository: project pages describe the applications themselves, and posts provide short public-facing case studies drawn from selected examples. Comments are available if someone wants to respond to a post, but interaction is optional. The primary goal is to make the work easy to review, understand, and discuss.
