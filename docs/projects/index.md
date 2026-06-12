---
title: Portfolio
comments: false
---

This page collects the application profiles in the portfolio. Each entry is designed to explain what the application does, how it works, and what technical capability it demonstrates.

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
				<h2 class="project-card-placeholder-title">Preview Coming Soon</h2>
				<p class="project-card-placeholder-note">{{ project.title }}</p>
			</div>
			{% endif %}
		</a>
		<p class="project-card-kicker">{{ project.category_label | default: 'Project' }}</p>
		<p class="project-card-meta">{{ project.access_label | default: 'Public repository' }}</p>
		<h2 class="project-card-title"><a href="{{ project.url | relative_url }}">{{ project.title }}</a></h2>
		<p class="project-card-summary">{{ project.summary }}</p>
		<p class="project-card-links">
			<a href="{{ project.url | relative_url }}">Open profile</a>
			{% if project.repo_visibility == 'public' and project.repo_url %}<a href="{{ project.repo_url }}">Repository</a>{% endif %}
		</p>
	</article>
	{% endfor %}
</section>
