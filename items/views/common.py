from items.models import Item, BookmarkletKey, Organization
from items.forms import (
    AddItemForm, BookmarkletKeyForm,
)

import logging, json
import requests

from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib.sites.models import Site
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def landing(request):
    """Our main landing page"""

    if request.user.is_authenticated():
        org = Organization.objects.get(user=request.user)
        context = {'org_slug': org.slug}
        context = RequestContext(request, context)
        
        return render_to_response('items.html', context)
    
    context = RequestContext(request, {})
    return render_to_response('landing.html', context)
    
    
    
def add_item(request):

    bookmarklet_key_id = request.GET.get('bookmarklet_key', '')
    try:
        bookmarklet_key = BookmarkletKey.objects.get(key=bookmarklet_key_id)
    except BookmarkletKey.DoesNotExist:
        return render_to_response('bookmarklet_denied.html')
    if not bookmarklet_key.is_active:
        return render_to_response('bookmarklet_denied.html')
    organization = bookmarklet_key.organization
    description = request.GET.get('description', '')
    link = request.GET.get('link', '')
    contributor = bookmarklet_key.display_name
    
    context = {'description':description, 
                'link':link,
                'bookmarklet_key':bookmarklet_key}
    context = RequestContext(request, context)
    
    return render_to_response('add_item.html', context)
        

def add_item_service(request):
    """Item submitted"""
    
    bookmarklet_key_id = request.POST['bookmarklet_key']
    try:
        bookmarklet_key = BookmarkletKey.objects.get(key=bookmarklet_key_id)
    except BookmarkletKey.DoesNotExist:
        return render_to_response('bookmarklet_denied.html')
    if not bookmarklet_key.is_active:
        return render_to_response('bookmarklet_denied.html')
        
    description = request.POST["description"]
    link = request.POST["link"]
    description = request.POST["description"]
    contributor = bookmarklet_key.display_name
    
    item = Item(bookmarklet_key=bookmarklet_key,
                link=link,
                description=description,
                contributor=contributor,)
    
    item.save()
    
    return HttpResponse('success', status=200)
        
        
def collaborator(request, bookmarklet_key_id):

    try:
        bookmarklet_key = BookmarkletKey.objects.get(key=bookmarklet_key_id)
    except BookmarkletKey.DoesNotExist:
        return render_to_response('bookmarklet_denied.html')
        
    organization = bookmarklet_key.organization
    bookmarklet_domain = Site.objects.get_current().domain

    if not bookmarklet_key.is_active:
        return render_to_response('bookmarklet_denied.html')


    context = {'bookmarklet_key': bookmarklet_key_id,
               'organization': organization, 'bookmarklet_domain': bookmarklet_domain}

    if request.method == 'POST':
        profile_form = BookmarkletKeyForm(request.POST, request.FILES, prefix='profile', instance=bookmarklet_key)    
        if profile_form.is_valid():

            profile = profile_form.save()
                
            return JsonResponse({'pic_url': profile.profile_pic.url})
        else:
            context['form'] = profile_form
            return render('collaborator.html', context)
    
    else:
        profile_form = BookmarkletKeyForm( prefix='profile', instance=bookmarklet_key)


    context['form'] = profile_form
    context = RequestContext(request, context)
    
    return render_to_response('collaborator.html', context)

def collaborator_confirm(request, bookmarklet_key_id):
    # Display the bookmarklet 

    context = {'bookmarklet_key': bookmarklet_key_id}
    return render_to_response('collaborator-confirm.html', context)

def bookmarklet(request, bookmarklet_key):
    """The bookmarklet"""
        
    bookmarklet_domain = Site.objects.get_current().domain

    return render_to_response('bookmarklet.js', {'bookmarklet_domain': bookmarklet_domain, 'bookmarklet_key': bookmarklet_key}, content_type='text/javascript')
