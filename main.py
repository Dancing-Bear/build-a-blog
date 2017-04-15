#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **args):
        self.response.write(*a, **args)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **args):
        self.write(self.render_str(template, **args))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.render("base.html")

class MainBlogHandler(Handler):
    def get(self):
        posts = db.GqlQuery("""SELECT * FROM BlogPost
                            ORDER BY created DESC LIMIT 5""")
        self.render("mainblog.html", posts=posts)

class NewPostHandler(Handler):
    def render_newpost(self, title="", body="", error=""):
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = BlogPost(title = title, body = body)
            post.put()
            post_id_str = str(post.key().id())
            self.redirect("/blog/" + post_id_str)
        else:
            error = "You need a title and a body!"
            self.render_newpost(title, body, error)

class ViewPostHandler(Handler):
    def render_viewpost(self, post="", error=""):
        self.render("viewpost.html", post=post, error=error)

    def get(self, id):
        post = BlogPost.get_by_id(int(id))
        if post:
            self.render_viewpost(post)
        else:
            error = "Sorry, there's no post by that ID."
            self.render_viewpost(post, error)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPostHandler),
    ('/blog', MainBlogHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
