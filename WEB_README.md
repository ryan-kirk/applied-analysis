# Website README

## Overview

This repository includes a small static website in `docs/` that is structured for a GitHub Pages project site.

Based on the current files, the site is designed to publish at:

- `https://ryan-kirk.github.io/applied-analysis/`

That URL comes from:

- `docs/_config.yml`
  - `url: https://ryan-kirk.github.io`
  - `baseurl: /applied-analysis`

There is no custom website build pipeline checked into this repository. The current setup appears to rely on GitHub Pages' built-in Jekyll build using the `docs/` folder as the site source.

## Current Site Architecture

- `docs/_config.yml`
  - Defines the site title, description, project-site `baseurl`, Markdown engine, permalink style, and the `jekyll-feed` plugin.
  - Defines a `projects` collection that outputs repository profile pages under `/projects/`.
  - Applies the `default` layout to posts and project pages, with comments enabled on posts by default.

- `docs/index.md`
  - Serves as the home page.
  - Uses Markdown plus inline HTML and Liquid to render the positioning statement, author section, project previews, recent case studies, and site description.

- `docs/_layouts/default.html`
  - Serves as the shared layout for the home page, project pages, and posts.
  - Pulls in `{{ '/assets/main.css' | relative_url }}`, which comes from the configured Jekyll theme rather than a committed local CSS file.
  - Contains most of the site's custom visual styling as inline CSS and uses `aa-` prefixed classes to avoid collisions with the Minima theme.
  - Renders the header, navigation, body content, footer, and the giscus comments embed.

- `docs/_projects/`
  - Contains one Markdown file per portfolio project or repository profile.
  - Each project page can carry its own summary, category label, order, and repository link.

- `docs/projects/index.md`
  - Serves as the portfolio index page for repository-level project profiles.

- `docs/_posts/`
  - Contains one Markdown file per published article.
  - Filenames follow the standard Jekyll post format: `YYYY-MM-DD-slug.md`.
  - Front matter controls the title, excerpt, preview image, and image alt text.

- `docs/assets/images/`
  - Stores the website-owned images used by posts and the home page.
  - Currently holds the post preview charts, author headshot, and QR image.

## Current Capabilities

The current website supports the following:

- A branded home page with:
  - positioning statement for the portfolio
  - author headshot
  - author bio
  - QR image for contact
  - automatically generated project cards
  - automatically generated recent-post cards
  - short "About This Site" section

- A primary navigation with:
  - home link
  - projects link

- A project index driven by `site.projects`
  - project profile cards render automatically from the collection
  - each card can show a category label, title, summary, and repository link

- Individual project pages with:
  - project title
  - summary
  - Markdown body content
  - optional repository link
  - link back to the projects index

- A post index driven by `site.posts`
  - posts render newest first
  - each card can show a preview image, publication date, title, and excerpt

- Individual post pages with:
  - title
  - published date
  - hero image
  - Markdown body content
  - link back to the home page

- Responsive layout behavior
  - the author section and post cards collapse to one column on smaller screens

- Comments on posts through giscus
  - powered by GitHub Discussions
  - configured in `docs/_layouts/default.html`

- Feed generation through `jekyll-feed`
  - when built by Jekyll/GitHub Pages, a feed should be generated automatically

- Project-site-safe URLs
  - the site uses Liquid `relative_url` filters so links and image paths respect `/applied-analysis`

## Current Content Inventory

At the time of this review, the site contains:

- 1 home page: `docs/index.md`
- 1 project index page: `docs/projects/index.md`
- 1 project profile in `docs/_projects/`
- 6 published posts in `docs/_posts/`
- 8 images in `docs/assets/images/`

The six current posts map closely to repository examples:

1. `2026-04-21-rates-moved-into-a-higher-environment.md`
   Source example: `examples/trend_signal/`
2. `2026-04-30-more-kidney-transplants-but-persistent-waitlist-pressure.md`
   Source example: `examples/kidney_transplant_signal_comparison/`
3. `2026-05-08-when-food-imports-became-a-system-pressure-signal.md`
   Source example: `examples/agriculture_system_pressure_africa/`
4. `2026-05-14-events-and-capital-costs-around-food-system-pressure.md`
   Source example: `examples/ssa_agricultural_capital_pressure/`
5. `2026-05-22-when-cheap-tokens-get-expensive.md`
   Source example: `examples/token_economics_orchestration/`
6. `2026-06-01-can-ai-infrastructure-keep-up.md`
   Source example: `examples/ai_compute_constraints/`

Each post currently:

- opens with a chart image
- summarizes the example in plain language
- links back to the corresponding `examples/` folder
- links to the example's `INSIGHT.md`

## Current Limitations

The website is intentionally simple, but there are some important constraints in the current setup:

- There is no checked-in `Gemfile`.
- There is no checked-in GitHub Actions workflow for the website.
- There is no automatic sync from `examples/` into `docs/_posts/` or `docs/assets/images/`.
- Additional repository profiles in `docs/_projects/` still need to be authored manually.
- Most custom styling lives inline inside `docs/_layouts/default.html`, not in a dedicated stylesheet.
- The site currently has no search, pagination, or post categories surfaced in the UI.

## How the Site Is Likely Published

The repository structure strongly suggests the following GitHub Pages setup:

1. The repository default branch is connected to GitHub Pages.
2. GitHub Pages is configured to publish from the `docs/` directory.
3. Pushing changes to `docs/` on the publishing branch triggers a Jekyll rebuild.

To confirm that in GitHub:

1. Open the repository on GitHub.
2. Go to `Settings`.
3. Open `Pages`.
4. Verify that the source is the default branch and the `/docs` folder.

If that Pages setting changes, the website may stop updating even if the `docs/` files remain correct.

## How to Preview the Site Locally

### Important note

This repo does not currently include a pinned local Jekyll environment. On this machine, `ruby` and `bundler` are available, but `jekyll` is not currently installed.

That means local preview requires a separate Jekyll installation.

### One common local setup

Install the required gems in your user Ruby environment:

```bash
gem install jekyll bundler minima jekyll-feed
```

Then, from the repository root, serve the site from `docs/`:

```bash
jekyll serve --source docs
```

Because `_config.yml` sets `baseurl: /applied-analysis`, the local preview URL will usually be:

```text
http://127.0.0.1:4000/applied-analysis/
```

If you want a simpler root-path local preview, you can usually override the base URL:

```bash
jekyll serve --source docs --baseurl ""
```

Then open:

```text
http://127.0.0.1:4000/
```

## How to Update the Home Page

Use these files depending on what you want to change:

- Update site title, description, base URL, or plugins:
  - `docs/_config.yml`

- Update the home page content and structure:
  - `docs/index.md`

- Update the project collection and project index:
  - `docs/_projects/`
  - `docs/projects/index.md`

- Update shared layout, typography, spacing, header, footer, and comment embed:
  - `docs/_layouts/default.html`

- Replace author images:
  - `docs/assets/images/ryan-kirk-headshot-circle.png`
  - `docs/assets/images/ryan-kirk-qr.png`

## How to Add a New Post

The current website workflow is manual and content-first.

1. Create or update the analysis in `examples/<example_name>/`.
2. Generate the final chart or illustration for that example.
3. Copy the website-ready image into `docs/assets/images/`.
4. Create a new post file in `docs/_posts/` using this naming pattern:

```text
YYYY-MM-DD-slug.md
```

5. Add front matter similar to this:

```yaml
---
title: Clear Post Title
comments: true
excerpt: One short summary sentence for the home-page card.
image: /assets/images/example-image.png
image_alt: Short accessible description of the image.
---
```

`comments: true` is already the default for posts in `docs/_config.yml`, but keeping it in the post front matter is consistent with the current files and makes the behavior explicit.

6. Add the hero image near the top of the post body:

```md
![Accessible image description]({{ '/assets/images/example-image.png' | relative_url }})
```

7. Write the post body in Markdown.
8. Link back to:
  - the example folder in `examples/`
  - the example's `INSIGHT.md`
9. Preview locally with Jekyll if available.
10. Commit and push the changes so GitHub Pages can rebuild the site.

## How to Add a New Project Page

Repository profiles now live in the `projects` collection.

1. Create a new file in `docs/_projects/`:

```text
docs/_projects/<project-slug>.md
```

2. Add front matter similar to this:

```yaml
---
title: Project Name
category_label: Applied AI
summary: One short summary sentence for the project card and page intro.
repo_url: https://github.com/ryan-kirk/project-name
order: 20
comments: false
---
```

3. Write the project description in Markdown.
4. Explain:
  - what the application does
  - how it is structured
  - why it matters
  - where the source repository lives
5. Preview locally with Jekyll if available.
6. Commit and push the changes.

The project will then appear automatically on:

- the home page project section
- the `/projects/` index page

## How to Update an Existing Post

1. Edit the relevant file in `docs/_posts/`.
2. If the chart changed, replace or rename the image in `docs/assets/images/`.
3. Update `image` and `image_alt` in the front matter if needed.
4. Keep the `excerpt` concise, because it appears on the home page.
5. If you rename the post file, the public URL slug will change.

## Website Conventions to Keep

These conventions are already used throughout the current site and are worth preserving:

- Use `{{ ... | relative_url }}` for internal links and assets.
- Keep post images inside `docs/assets/images/` so the site owns its published media.
- Use web-safe filenames for images and post slugs.
- Keep post excerpts short and readable, since they render on the home page.
- Include clear alt text for every image.
- Keep each post tightly tied to one repository example.

## Comments and Discussion Configuration

Post comments are embedded through giscus in `docs/_layouts/default.html`.

If the GitHub repository, discussion category, or comment behavior changes, update the `data-*` attributes inside the giscus `<script>` block in that file.

## Recommended Future Improvements

If you want this site to be easier to maintain, the highest-value improvements would be:

1. Add a `Gemfile` so local preview uses a documented, repeatable Jekyll environment.
2. Add a short publish checklist or script that copies final example images into `docs/assets/images/`.
3. Move most inline CSS from `docs/_layouts/default.html` into a dedicated stylesheet for cleaner maintenance.
4. Add a lightweight validation step to catch broken internal links or missing images before publishing.

## Short Summary

The website is currently a lightweight GitHub Pages + Jekyll layer on top of this repository's analytical examples. The `examples/` directories remain the source of truth for the analysis, while `docs/` contains the manually curated public-facing homepage, posts, and published images.
