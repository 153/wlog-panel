#/usr/bin/env python3
import os, time, cgi, cgitb
import re, string
import webtools as wt
import mistune

markdown = mistune.Markdown()
cgitb.enable()

sett = {'pw': "dank", 
        'url':"./admin.py3?", 
        'dir':"../pages/",
        'ext':".md",
        'dpre': "date: "}

def panel():
    modes = {'p_add':'addpost()', 'p_edit':'editpost()', 'p_del':'delpost()',
             'p_move':'movepost()', 'c_add':'categoryadd()',
             'c_del':'categorydel()', 'logout':'logout()'}
    print("<div>")
    print(sorted([modes[i] for i in modes.keys()]))
    print("<p>")
    if not wt.get_form('m') in modes.keys():
        with open("main.html", 'r') as mainpanel:
            mainpanel = mainpanel.read().splitlines()
        mainpanel = "<br>".join(mainpanel)
        print(mainpanel.format(sett['url']))
    else:
        print("<h1>",wt.get_form('m'),"</h1>")
        print("<small><a href='{0}'>".format(sett['url']))
        print("&lt;&lt; back</a></small><p>")
        eval(modes[wt.get_form('m')])
    print("</div>")

def indexposts():
    postindex = []
    files = [x for x in os.walk(sett['dir'])]
    for x in files:
        for y in x[2]:
            if y[-len(sett['ext']):] == sett['ext']:
                postindex.append(x[0] + "/" + y)
    return postindex
    
def logged_in(password=''):
    if not password:
        if not wt.get_form("pw"):
            print(wt.new_form(sett['url'], 'post'))
            print(wt.put_form('password', 'pw', ''))
            print(wt.put_form('submit', '', "Login"), "</form>")
            return
        password = wt.get_form("pw")
    if password != sett['pw']:
        print("You need to enter a valid password to continue.")
        print("<a href='{0}pw='>Login</a>".format(sett['url']))
    else:
        return 1

def logout():
    print("You have been logged out successfully.<p>")
    print("<a href='{0}'>&lt;&lt; Back</a>".format(sett['url']))
    print(wt.put_cookie('pw', ''))

def subdir_list():
    form = []
    subdirs = catlist()
    menu = wt.dropdown('subd', subdirs)
    menu = menu.splitlines()
    menu.insert(1, "<option value=''> -----</option>")
    menu = '\n'.join(menu)
    if wt.get_form('subd') in subdirs:
        menu = menu.replace("<option value='" + wt.get_form('subd'),
                     "<option selected value='" + wt.get_form('subd'))
    return menu
            
def getpost(p_fn=''):
    posts = indexposts()
    if not wt.get_form('date') or wt.get_form('date') == 'now':
        date = wt.fancy_time('', 'human')
    else:
        date = wt.get_form('date')
    pps = [wt.get_form('fn')[:13],
           wt.get_form('title')[:30],
           date,
           wt.get_form('content')[:100000]]
    pps[0] = re.sub(r'[^\w\s]', '', pps[0])
    pps[0] = re.sub(r'\s+', '_', pps[0])
    if p_fn in posts:
        with open(p_fn, 'r') as entry:
            entry = entry.read().splitlines()
        ds = [p_fn,
              entry[1],
              entry[0][6:], # strip `date: '
              '\n'.join(entry[2:])]
        for n, i in enumerate(pps):
            if not pps[n]:
                pps[n] = ds[n]
    return pps
    
def addpost():
    print(wt.new_form(sett['url'] + "#edit", 'post'))
    print(wt.put_form('hidden', 'm', 'p_add'))
    ind = [i[len(sett['dir']):-len(sett['ext'])] for i in indexposts()]
    tryfn = ''
    if wt.get_form('subd'):
        tryfn += wt.get_form('subd') + "/"
    if wt.get_form('fn'):
        tryfn += wt.get_form('fn')        
    if tryfn in ind:
        print("Sorry, entry {0} exists.".format(tryfn))
        print("<br>If you would like, <p>")
        print("<a href='{0};m=p_edit;fn={1}'>edit it</a>".format(
            sett['url'], sett['dir'] + tryfn + sett['ext']))
        print("</form>")
        return None
    with open("post.html", "r") as post:
        post = post.read()
    if wt.get_form('fn'):
        mp = getpost(wt.get_form('fn'))
        mp[2].replace("&gt;", ">").replace("&lt;", "<")
        mp[0], mp[1] = mp[1], mp[0]
        mp[1], mp[2] = mp[2], mp[1]
        mp.append(subdir_list())
        mp.append(markdown(mp[3]))
        subd = ''
        if wt.get_form('subd'):
            sfubd = wt.get_form('subd') + "/"
        newfn = sett['dir'] + subd + mp[2] + sett['ext']
        if wt.get_form('sub'):
            mp[1] = sett['dpre'] + mp[1]
            mp.pop(2)
            mp[1], mp[0] = mp[0], mp[1]
            with open(newfn, "x") as newf:
                buff = '\n'.join(mp[:3])
                newf.write(buff)
            print("Written successfully!")
            print("<p><code>" + newfn + "</code>")
        else:
            print(post.format(*mp))
    else:
        print(post.format('', wt.fancy_time('', 'human'), '',
                          '', subdir_list(), ''))
    print("</form>")

def editpost(p_fn=''):
    postindex = indexposts()
    pps = [wt.get_form('fn'), 
           wt.get_form('title'),
           wt.get_form('date'),
           wt.get_form('content').replace("&gt;", ">").replace("&lt;", "<")]
    print(wt.new_form(sett['url'] + "#edit", 'post'))
    print(wt.put_form('hidden', 'm', 'p_edit'))
    if pps[0]:
        if wt.get_form('prev'):
            print("Previewing")
        print(wt.get_form("fn"))
        fn = wt.get_form("fn")
        print("<p>")
        with open(fn, 'r') as entry:
            entry = entry.read().splitlines()
        ds = [pps[0], entry[1], entry[0][6:],
              '\n'.join(entry[2:])]
        for n, i in enumerate(pps):
            if not pps[n]:
                pps[n] = ds[n]
        pps[2], pps[1] = pps[1], pps[2]
        if wt.get_form('sub'):
            with open(pps[0], 'w') as pos:
                pps[1] = sett['dpre'] + pps[1]
                blog = '\n'.join(pps[1:])
                pos.write(blog)
            print("<p>Blog entry<i>", pps[2], "</i>updated successfully.")
            return None
        pps[0], pps[2] = pps[2], pps[0]
        pps.append('')
        pps.append(markdown(pps[3]))
        with open("post.html", "r") as pos:
            pos = pos.read().replace("fn'", "fn' readonly ")
        print(pos.format(*pps))

    postnames = [i[len(sett['dir']):-len(sett['ext'])] for i in postindex]
    if not wt.get_form('fn'):
        print(wt.dropdown('fn', postindex, postnames))
        print(wt.put_form('submit', '', 'go'))
    print("</form>")

def delpost():
    fn_ind = indexposts()
    p_ind = [i[len(sett['dir']):-len(sett['ext'])] for i in fn_ind]
    print(wt.new_form(sett['url'], 'post'),
          wt.put_form('hidden', 'm', 'p_del'))
    if wt.get_form('fil'):
        filz = wt.get_form('fil').split('\n')
        for n, i in enumerate(filz):
            if i[len(sett['dir']):-len(sett['ext'])] not in p_ind:
                continue
            else:
                os.remove(i)
                print("<br>Deleted", i)
    for n, i in enumerate(p_ind):
          print("<br>", wt.put_form("checkbox", 'fil', fn_ind[n]), i)
    print("<p>", wt.put_form("submit", "sub", "Submit"), "</form>")
#        print(filz)
        
def catlist():
    dirs = []
    for root, di, fi in os.walk(sett['dir']):
        if len(di) > 0:
            dirs.append(di)
    return sorted(dirs[0])

def categoryadd():
    if wt.get_form('add') or wt.get_form('add1'):
        ndir = wt.get_form('dir')[:12]
        ndir = re.sub(r'[^\w\s]', '', ndir)
        ndir = re.sub(r"\s+", "_", ndir)
        print(sett['dir'] + ndir + "/")
        if ndir in catlist():
            print("It exists already.<p>")
        elif not wt.get_form('add1'):
            print("<p><i>Confirm?</i>",
                  wt.new_form(sett['url'], 'post'),
                  wt.put_form('hidden', 'm', 'c_add'),
                  wt.put_form('hidden', 'dir', ndir),
                  wt.put_form("submit", "add1", "Create"),
                  "</form>")
            print("<p>")
            
        elif ndir not in catlist():
            os.makedirs(sett['dir'] + ndir)
            print(ndir, "created successfully.<p>")
        
    print("Current categories:<br>")
    print("<ul>")
    clist = catlist()
    for n, i in enumerate(clist):
        clist[n] = "<li>" + i + " " \
            + "(" + str(len(os.listdir(sett['dir'] + i))) + ")"
    print("\n".join(clist))
    print("</ul>")
    print(wt.new_form(sett['url'], 'post'),
          wt.put_form('hidden', 'm', 'c_add'),
          wt.put_form('text', 'dir'),
          wt.put_form('submit', 'add', 'Add'),
          "</form>")
    
def main():
    cookies = wt.get_cookie()
    pw = ''
    print(wt.head("admin panel"))
    print("<link rel='stylesheet' type='text/css' href='admin.css'>")
    print("<body>")
    if 'pw' in cookies.keys():
        pw = cookies['pw']
    if pw == sett['pw']:
        panel()
        print(wt.get_ip())
    elif logged_in(wt.get_form("pw")):
        print(wt.put_cookie('pw', wt.get_form("pw")))
        panel()
        
    if wt.get_form("m"):
        print(wt.get_form("m"))

main()
