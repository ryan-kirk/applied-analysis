---
title: Home
comments: false
---

<section class="home-positioning">
	<p class="home-positioning-kicker">Applied AI, analytics, and decision support</p>
	<h2 class="home-positioning-title">A working portfolio of analytical systems, public case studies, and practical software.</h2>
	<p class="home-positioning-copy">This homepage now acts as a working feed: recent portfolio entries, recent case studies, and the latest examples of how Ryan Kirk turns technical systems into usable decision support.</p>
</section>

## Recent Portfolio Entries

<p class="section-intro">The latest application profiles across analytics, decision support, geospatial exploration, research tooling, and workflow design.</p>

<section class="project-list">
	{% assign projects = site.projects | sort: 'order' %}
	{% for project in projects limit: 4 %}
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
<p class="section-link-row"><a href="{{ '/projects/' | relative_url }}">See all</a></p>

## Latest Case Studies

<p class="section-intro">Recent blog-style case studies drawn from the portfolio work, with public write-ups that explain the framing, signal, and practical takeaway.</p>

<section class="post-list">
	{% if site.posts.size > 0 %}
	{% for post in site.posts limit: 4 %}
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
<p class="section-link-row"><a href="{{ '/blog/' | relative_url }}">See all</a></p>
