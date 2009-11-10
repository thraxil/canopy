from django.db import models
from restclient import GET,POST,PUT,DELETE
import urllib2
from django.template.defaultfilters import slugify

TAHOE_BASE = "http://127.0.0.1:8123/uri/"
ROOT_CAP = "URI:DIR2:hkqdang4w3ctfa562kfvtwmtvy:ffoqs7qkga3o3lteham7vihpjkvo3n7k7q7rfvspj3hmlxmwwroa"

class TahoeDir(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField()
    cap = models.CharField(max_length=1024)

    def tahoe_url(self):
        return TAHOE_BASE + urllib2.quote(self.cap)

    def get_subdir(self,dirs):
        if len(dirs) == 0:
            return self
        first = dirs[0]
        for child in self.children():
            if first == child.slug:
                return child.get_subdir(dirs[1:])
        print "should raise a 404 here"

    def children(self):
        return [id.child for id in InDir.objects.filter(parent=self)]

    def num_children(self):
        return InDir.objects.filter(parent=self).count()

    def has_children(self):
        return self.num_children() > 0

    def mkdir(self,name):
        slug = slugify(name)
        cap = POST(self.tahoe_url(),params=dict(t="mkdir",name=name),async=False)
        d = TahoeDir.objects.create(name=name,slug=slug,cap=cap)
        indir = InDir.objects.create(parent=self,child=d,ordinality=self.num_children() + 1)
        return d

    def parent(self):
        r = InDir.objects.filter(child=self)
        if r.count() == 0:
            return None
        else:
            return r[0].parent

    def get_absolute_url(self):
        p = self.parent()
        if p is None:
            return "/"
        else:
            return p.get_absolute_url() + self.slug + "/"

    def num_files(self):
        return self.tahoefile_set.count()

    def has_files(self):
        return self.num_files() > 0

    def add_file(self,file):
        filename = file.name
        POST(self.tahoe_url(),params=dict(t="upload"),
             files=dict(file=dict(filename=file.name,file=file.read())),
             async=True)
        return TahoeFile.objects.create(filename=file.name,dir=self,
                                        slug=slugify(file.name),
                                        ordinality=self.num_files() + 1)



class InDir(models.Model):
    parent = models.ForeignKey(TahoeDir,related_name='parent_dir')
    child = models.ForeignKey(TahoeDir,related_name='child_dir')
    ordinality = models.IntegerField(default=1)

class TahoeFile(models.Model):
    filename = models.CharField(max_length=256)
    dir = models.ForeignKey(TahoeDir)
    slug = models.SlugField()
    ordinality = models.IntegerField(default=1)

    def get_absolute_url(self):
        return self.dir.get_absolute_url() + 


def get_root():
    try:
        r = TahoeDir.objects.get(name="__ROOT__")
        return r
    except TahoeDir.DoesNotExist:
        # need to create one
        return TahoeDir.objects.create(name="__ROOT__",slug="root",cap=ROOT_CAP)
