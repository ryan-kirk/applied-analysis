---
title: Projects
comments: false
---

This page collects repository profiles for the portfolio. Each profile is meant to answer a simple question: what does the application do, how is it structured, and why does it matter? The current working list includes public repositories and provisional private entries pending review.

<section class="project-list">
	{% assign projects = site.projects | sort: 'order' %}
	{% for project in projects %}
	<article class="project-card">
		<p class="project-card-kicker">{{ project.category_label | default: 'Project' }}</p>
		<p class="project-card-meta">{{ project.access_label | default: 'Public repository' }}</p>
		<h2 class="project-card-title"><a href="{{ project.url | relative_url }}">{{ project.title }}</a></h2>
		<p class="project-card-summary">{{ project.summary }}</p>
		<p class="project-card-links">
			<a href="{{ project.url | relative_url }}">Open profile</a>
			{% if project.repo_url %}<a href="{{ project.repo_url }}">Repository</a>{% endif %}
		</p>
	</article>
	{% endfor %}
</section>

Additional repository profiles can be added by creating new Markdown files in `docs/_projects/`.
