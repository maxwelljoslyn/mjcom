"""Personal website for Maxwell Joslyn."""

import pendulum
import web
from understory import auth, code, data, editor, media, owner, posts
from understory.posts import PostNotFoundError

app = web.application(
    __name__,
    db=True,
    args={
        "year": r"\d{4}",
        "month": r"\d{2}",
        "day": r"\d{2}",
        "post_id": web.nb60_re + r"{,4}",
        "slug": r"[\w_-]+",
        "category": r"[\w\d_-]+",
    },
    mounts=[
        auth.client.app,
        auth.server.app,
        code.app,
        data.app,
        editor.app,
        media.app,
        owner.app,
        posts.app,
    ],
)


@app.control("")
class Home:
    """Profile and primary feed."""

    def get(self):
        """Render a profile summary and a reverse chronological feed of public posts."""
        return app.view.home(posts.app.model.get_posts())
        # return app.view.index(posts.app.model.read("/consulting"))


@posts.app.query
def get_post_by_old_mjcom_path(db, path):
    try:
        resource = db.select(
            "resources, json_each(resources.resource, '$.url')",
            what="resource, json_extract(resource, '$.url') as url",
            where="json_each.value = ?",
            vals=[path],
        )[0]
    except IndexError:
        raise PostNotFoundError(path)


# @app.control("({year}/{month}/{day}/{post_id}(/{slug})?)|([\w\d-]+)", try_late=True)
@app.control("({year}/{month}/{day}/{post_id})|([\/\w\d-]+)", try_late=True)
class Permalink:
    """An individual entry."""

    redirects = {"thedrongo/interviews": "/thedrongo"}

    def get(self, year=None, month=None, day=None, post_id=None):
        """"""

        path = web.tx.request.uri.path
        if new_path := self.redirects.get(path):
            raise web.SeeOther(new_path)

        try:
            resource = web.application(
                "understory.posts"
            ).model.get_post_by_old_mjcom_path(web.tx.request.uri.path)["resource"]
        except PostNotFoundError:
            try:
                resource = web.application("understory.posts").model.read(
                    web.tx.request.uri.path
                )["resource"]
            except PostNotFoundError:
                web.header("Content-Type", "text/html")
                raise web.NotFound(app.view.post_not_found())
        if resource["visibility"] == "private" and not web.tx.user.session:
            raise web.Unauthorized(f"/auth?return_to={web.tx.request.uri.path}")
        # mentions = web.indie.webmention.get_mentions(str(web.tx.request.uri))
        # TODO FIXME this won't work if we access by an old mjcom path and Y/M/D/trailer all None
        return app.view.entry(
            f"/{year}/{month}/{day}/{post_id}", resource
        )  # , mentions)


@app.control("(categories|category|tags)")
class Categories:
    def get(self):
        if not web.tx.request.uri.path.startswith("categories"):
            # plural is canonical; "tags" is from previous version of site
            raise web.SeeOther("/categories")
        return app.view.categories(
            web.application("understory.posts").model.get_categories()
        )


@app.control("(categories|category|tags|tag)/{category}")
class Category:
    def get(self, category):
        if not web.tx.request.uri.path.startswith("categories"):
            # plural is canonical; "tags" is from previous version of site
            raise web.SeeOther(f"/categories/{category}")
        return app.view.category(
            web.application("understory.posts").model.get_posts(categories=[category])
        )


@app.control("{year}")
class Year:
    """All entries for a year."""

    def get(self, year):
        """."""
        year = int(year)
        dt = pendulum.datetime(year, 1, 1)  # January 1 of year
        previous_year = dt.subtract(years=1)
        next_year = dt.add(years=1)
        relevant_posts = posts.app.model.get_posts(
            after=f"{previous_year.year}-12-31", before=f"{next_year.year}-01-01"
        )
        return app.view.year(dt.year, relevant_posts)


@app.control("{year}/{month}")
class Month:
    """All entries for a month."""

    def get(self, year, month):
        """."""
        year, month = int(year), int(month)
        dt = pendulum.datetime(year, month, 1)  # 1st of month in year
        previous_month = dt.subtract(months=1)
        next_month = dt.add(months=1)

        relevant_posts = posts.app.model.get_posts(
            after=f"{previous_month.year}-{previous_month.month:02d}-{previous_month.last_of('month').day:02d}",
            before=f"{next_month.year}-{next_month.month:02d}-01",
        )

        return app.view.month(dt.year, dt.month, relevant_posts)


@app.control("{year}/{month}/{day}")
class Day:
    """All entries for a day."""

    def get(self, year, month, day):
        """."""
        year, month, day = int(year), int(month), int(day)
        dt = pendulum.datetime(year, month, day)
        previous_day = dt.subtract(days=1).set(hour=23, minute=59, second=59)
        next_day = dt.add(days=1)

        relevant_posts = posts.app.model.get_posts(
            after=f"{previous_day.year}-{previous_day.month:02d}-{previous_day.day:02d}T{previous_day.hour:02d}:{previous_day.minute:02d}:{previous_day.second:02d}",
            before=f"{next_day.year}-{next_day.month:02d}-{next_day.day:02d}",
        )
        return app.view.day(year, month, day, relevant_posts)


# LIVE
# DONE reverse engineer homepage content from mxjn.me
# DONE write redirect route, starting with thedrongo/interviews -> thedrongo
# DONE fix / remove breadcrumbs on month and day pages
# DONE links on entry.html if X then X for X in published, updated, categories
# DONE imp category pages using jsoneach approach, similar to old permalink redirect
# DONE redirect tags -> categories
# TODO reverse engineer drongo template from mxjn.me
# TODO reverse engineer entry template from mxjn.me
# TODO reverse engineer homepage nav from mxjn.me
# TODO reverse engineer poem template from mxjn.me
# TODO varying redirects like /td/interview/xyz (no s on interviews), /poem/xyz -> /poems/xyz, etc
# LATER
# TODO Fix SLC image links in individual posts and in the (current version of) the SLC main page ; thereafter, don't display individual SLC entries in blog/feed?
# TODO 0th entry in url list is y/m/d/trailer; others are redirected  rel=canonical on angelo y/m/d/id links to old link, if present
# TODO implement app.view.post_not_found()
# TODO def has_nicelink? if len(url) > 1 and ... uh ... how do I distinguish nicelinks from US default links from "this used to be the path to this post but there's a new one now; this OLD path shoud redirect?!" e.g. if url = ['y/m/d/id', 'old/nice/path', 'new/new/path'] ... can redirect function handle all of those easily?
