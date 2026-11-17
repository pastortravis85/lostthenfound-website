# Lost Then Found Ministries — Pages CMS website

This repository preserves the Adventure & Discovery design in `template.html` and uses Pages CMS to edit content.

## Cloudflare Pages build settings
- Framework preset: None
- Production branch: main
- Build command: `pip install -r requirements.txt && python build.py`
- Build output directory: `public`

## Content
- Devotionals: `content/devotionals/*.md`
- Pastor resources: `content/pastor-resources/*.md`
- Journal: `content/journal/*.md` (only `published: true` appears on the site)
- Settings: `content/site.json`
- Uploaded media: `media/`

In Pages CMS, add entries and commit. Cloudflare automatically rebuilds after each GitHub commit.

The old `index.html` is replaced by `template.html` and the build generates a new `public/index.html`. Do not manually edit `public/`.

## Launch notes
- PDF and Amazon links display only when supplied.
- Shop and donations remain placeholders until real providers and legal setup are complete.
- Keep the original Cloudflare Direct Upload project running while testing this new Git-connected project.
- Review permission to redistribute Scripture quotations and any KDP Select exclusivity before uploading complete books.
