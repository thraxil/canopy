from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import datetime

def get_dir(path):
    dir = None
    root = get_root()
    if path == "":
        dir = root
    else:
        path = path.strip("/")
        dirs = path.split("/")
        dir = root.get_subdir(dirs)
    return dir

def dir(request,path):
    return render_to_response("dir.html",dict(dir=get_dir(path)))

def mkdir(request,path):
    dir = get_dir(path)
    if dir is not None:
        d = dir.mkdir(request.POST.get('name','new directory'))
        return HttpResponseRedirect(d.get_absolute_url())

def upload(request,path):
    dir = get_dir(path)
    if dir is not None:
        f = dir.add_file(request.FILES['file'])
        return HttpResponseRedirect(dir.get_absolute_url())
