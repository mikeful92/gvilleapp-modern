"""Custom staticfiles storage that tolerates dangling url(...) refs in vendored CSS.

Background
----------
We vendor Bootstrap 3.4.1's ``bootstrap.min.css`` and ``bootstrap-theme.min.css``
in ``static/static_dirs/css/``, but not the rest of the Bootstrap distribution.
Specifically, the CSS files reference:

* ``../fonts/glyphicons-halflings-regular.{eot,svg,ttf,woff,woff2}`` — Glyphicons
  font files. Our templates use Font Awesome icons, not Glyphicons, so the fonts
  are never actually requested by any rendered page.
* ``bootstrap-theme.min.css.map`` — a CSS source map, only fetched by devtools.

In a browser these missing files would just 404 silently. But in production
we use ``CompressedManifestStaticFilesStorage`` (via WhiteNoise) to fingerprint
and compress static files. Its ``post_process`` step walks every CSS file,
parses every ``url(...)``, and expects each one to resolve to a real file on
disk so it can hash + rewrite the reference. The first dangling ref aborts
``collectstatic`` with::

    whitenoise.storage.MissingFileError: The file 'fonts/glyphicons-...' could
    not be found with <...CompressedManifestStaticFilesStorage object>

Why ``manifest_strict = False`` doesn't fix this
-----------------------------------------------
``manifest_strict`` (and WhiteNoise's ``WHITENOISE_MANIFEST_STRICT`` mirror) is
checked in ``ManifestFilesMixin.stored_name`` — the **runtime** path used when
serving requests after ``collectstatic`` has finished. The collect-time error
comes from a different path: ``url_converter`` → ``_stored_name`` →
``hashed_name``, which raises ``ValueError`` from the ``self.exists(filename)``
check before any manifest_strict logic runs. WhiteNoise just reformats that
ValueError into the more helpful ``MissingFileError``.

The standard community workaround for this (attested in WhiteNoise issues #96
and #291, DRF issues #2008 and #4950, and elsewhere) is to override
``hashed_name`` to swallow the ValueError for dangling refs and leave them as
the original un-hashed URL. Files that *do* exist still get fingerprinted and
rewritten normally; only the dangling refs stay as-is.

When to delete this file
------------------------
Remove this module (and revert ``STORAGES`` in ``settings.py`` to the stock
``whitenoise.storage.CompressedManifestStaticFilesStorage``) once Bootstrap is
replaced or the missing Glyphicons fonts + ``.css.map`` files are vendored.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class TolerantCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content=content, filename=filename)
        except ValueError:
            # Dangling url(...) ref in a vendored CSS file — see module docstring.
            return name
