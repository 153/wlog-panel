#/usr/bin/env python3
import os, time, cgi, cgitb
import re, string, shutil
import webtools as wt
import mistune

markdown = mistune.Markdown()
cgitb.enable()

def sett():
    settt = {}
    with open("sett.txt", 'r') as sett:
        sett = sett.read().splitlines()
    for i in sett:
        i = i.split(" ")
        if len(i) < 2 or i[0] in ["", " ", "#"]:
            continue
        if len(i) > 2:
            i[1] = " ".join(i[1:])
        settt[i[0]] = i[1]
    return settt

sett = sett()
if sett['t_f']:
    wt.time_form = sett['t_f']
        
def panel():
    if wt.get_form('m'):
        print("<small><a href='{0}'>".format(sett['url']))
        print("&lt;&lt; back</a></small><p>")
        print("<div class='panel'>")
    else:
        print("<div class='panel'>")
        print("<h1>Admin Panel</h1>")
    modes = {'p_add':'addpost()', 'p_edit':'editpost()',
             'p_del':'delpost()', 'p_move':'movepost()',
             'c_add':'categoryadd()', 'c_del':'categorydel()',
             'settings':'settings()', 'logout':'logout()'}
#    print(sorted([modes[i] for i in modes.keys()]))
    if not wt.get_form('m') in modes.keys():
        with open("main.html", 'r') as mainpanel:
            mainpanel = mainpanel.read().splitlines()
        mainpanel = "\n<br>".join(mainpanel)
        print(mainpanel.format(sett['url']))
    else:
#        print("<h1>",wt.get_form('m'),"</h1>")
        eval(modes[wt.get_form('m')])
    print("</div><p>")
    print("<small><a href='{0}'>".format(sett['url']))
    print("&lt;&lt; back</a></small><p>")

def indexposts():
    postindex = []
    files = [x for x in os.walk(sett['dir'])]
    for x in files:
        for y in x[2]:
            if y[-len(sett['ext']):] == sett['ext']:
                z = str(x[0] + "/" + y).replace("//", "/")
                postindex.append(z)
    return sorted(postindex)
    
def logged_in(password=''):
    # confirm login / Get n set the password 
    if not password:
        if not wt.get_form("pw"):
            print("""<style>input {height: 2.5em;font-size: 150%;}
input[password] {width: 12em;}</style><p><center>""")
            print(wt.new_form(sett['url'], 'post'),
                  wt.put_form('password', 'pw', ''),
                  wt.put_form('submit', '', "Login"),
                  "</form>")
            return
        password = wt.get_form("pw")
    if password != sett['pw']:
        print("You need to enter a valid password to continue.")
        print("<a href='{0}pw='>Login</a>".format(sett['url']))
    else:
        return 1

def logout():
    print("<h1>Logout</h1>")
    print("You have been logged out successfully.<p>")
    print("<a href='{0}'>&lt;&lt; Back</a>".format(sett['url']))
    print(wt.put_cookie('pw', ''))

def catlist():
    dirs = []
    for root, di, fi in os.walk(sett['dir']):
        if len(di) > 0:
            dirs.append(di)
    return sorted(dirs[0])
    
def subdir_list():
    subdirs = catlist()
    menu = wt.dropdown('subd', subdirs).splitlines()
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
        date = wt.get_form('date')[:30]
    pps = [wt.get_form('fn')[:13],
           date,
           wt.get_form('title')[:30],
           wt.get_form('content')[:100000]]
    pps[0] = re.sub(r'[^\w\s]', '', pps[0])
    pps[0] = re.sub(r'\s+', '_', pps[0])
    if p_fn in posts:
        with open(p_fn, 'r') as entry:
            entry = entry.read().splitlines()
        ds = [p_fn,
              entry[0][6:], # strip `date: '
              entry[1],
              '\n'.join(entry[2:])]
        for n, i in enumerate(pps):
            if not pps[n]:
                pps[n] = ds[n]
    return pps
    
def addpost():
    print("<h1>Add Post</h1>")
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
        mp[2] = mp[2].replace("&gt;", ">").replace("&lt;", "<")
        mp[0], mp[2] = mp[2], mp[0]
        mp.append(subdir_list())
        mp.append(markdown(mp[3]))
        subd = ''
        if wt.get_form('subd'):
            subd = wt.get_form('subd') + "/"
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

# need to refactor

def editpost(p_fn=''):
    print("<h1>Edit post</h1>")
    postindex = sorted(indexposts())
    pps = [wt.get_form('fn'), 
           wt.get_form('title'),
           wt.get_form('date'),
           wt.get_form('content').replace("&gt;", ">").replace("&lt;", "<")]
    print(wt.new_form(sett['url'] + "#edit", 'post'))
    print(wt.put_form('hidden', 'm', 'p_edit'))
    if pps[0]:
        if wt.get_form('prev'):
            print("Previewing")
        print("<code>", wt.get_form("fn"), "</code>")
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
        pps.append(markdown(pps[3].replace(sett['readmore'], "<hr>")))
        with open("post.html", "r") as pos:
            pos = pos.read().replace("fn'", "fn' readonly ")
        print(pos.format(*pps))

    postnames = [i[len(sett['dir']):-len(sett['ext'])] for i in postindex]
    if not wt.get_form('fn'):
        print(wt.dropdown('fn', postindex, postnames))
        print(wt.put_form('submit', '', 'go'))
    print("</form>")
    
def delpost():
    print("<h1>Delete posts</h1>")
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
    p_ind = [i[len(sett['dir']):-len(sett['ext'])] for i in indexposts()]
    for n, i in enumerate(p_ind):
          print("<br>", wt.put_form("checkbox", 'fil', fn_ind[n]), i)
    print("<p>", wt.put_form("submit", "sub", "Delete"), "</form>")

def movepost():
    print("<h1>Move posts</h1>")
    subd1 = wt.get_form('subd1')
    subd2 = wt.get_form('subd2')
    subds = [subd1, subd2]
    subdfs = [[],[]]
    for n, i in enumerate(subds):
        if i == '':
            bar = len(sett['dir'].split('/'))
            subdfs[n] = [i for i in indexposts() if len(i.split('/')) == bar]
        elif i in catlist():
            subdfs[n] = [j for j in indexposts() if i + "/" in j]
    if wt.get_form('conf'):
        if wt.get_form('subd1_'):
            moves = subdfs[0]
        elif wt.get_form('fn'):
            moves = wt.get_form('fn').split('\n')
        for i in moves:
                shutil.move(i, sett['dir'] + subds[1])
        print("<p>Finished moving")
        return

    print(wt.new_form('.', 'post'),
          wt.put_form('hidden', 'm', 'p_move'))
    print("<table>")
    print("<tr><th>From dir",
          "<th>--&gt;",
          "<th>To dir")
    s = subdir_list().replace('subd', 'subd1')
    if subds[0]:
        s = s.replace("'" + subds[0] + "'", \
                      "'" + subds[0] + "' selected")
    box = wt.put_form("checkbox", "subd1_", 1)
    if wt.get_form("subd1_"):
        box = box.replace(">", " checked>")
    print("<tr><td>", s, "All?", box, "<td><td>")
    s = subdir_list().replace('subd', 'subd2')
    if subds[1]:
        s = s.replace("'" + subds[1] + "'",
                      "'" + subds[1] + "' selected")
    print(s, "<tr><td colspan='3'>")
    if len(subds) != 2 or subds[0] == subds[1]:
        print(wt.put_form("submit", "sub", "Load"))
        print("\n<br>".join([
            "<p>Move all of the posts in 1 category into the other.",
            "If a post with the same filename exists in both",
            "directories, the post with the matching filename will",
            "remain in its source directory."]))
    else:
        print("Really move posts from `<i>" + subds[0] \
              + "</i>` to `<i>" + subds[1] + "</i>`?<p>")
        print("<center>", wt.put_form("submit", 'sub', 'Check'),
              "&emsp;", wt.put_form("submit", 'conf', "Move"),
              "</center>")
        for i in subdfs[0]:
            x = "<br>" + wt.put_form('checkbox', 'fn', i) +  i
            if i in wt.get_form('fn').split('\n'):
                x = x.replace("'>", "' checked>")
            print(x)
    print("</table></form>")

def categoryadd():
    print("<h1>Add Category</h1>")
    if wt.get_form('add') or wt.get_form('add1'):
        ndir = wt.get_form('dir')[:12]
        ndir = re.sub(r'[^\w\s]', '', ndir)
        ndir = re.sub(r"\s+", "_", ndir)
        if ndir in catlist():
            print("It exists already.<p>")
        elif not wt.get_form('add1'):
            print(sett['dir'] + ndir + "/")
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

def categorydel():
    print("<h1>Delete Category</h1>")
    if wt.get_form('del') or wt.get_form('del1'):
        ddir = wt.get_form('dir').replace("\r", "").split("\n")
        for n, i in enumerate(ddir):
            ddir[n] = re.sub(r'[^\w\s]', '', i)
            ddir[n] = re.sub(r"\s+", "_", i)
            print(sett['dir'] + i + "/")
        if not wt.get_form('del1'):
            print("<p><i>Confirm?</i>",
                  wt.new_form(sett['url'], 'post'),
                  wt.put_form('hidden', 'm', 'c_del'),
                  wt.put_form('hidden', 'dir', '\n'.join(ddir)),
                  wt.put_form('submit', 'del1', "Delete"),
                  "</form>")
        else:
            for i in ddir:
                if not i in catlist():
                    continue
                i = sett['dir'] + i
                if len(os.listdir(i)) == 0:
                    os.rmdir(i)
                    print("<br>Deleted", i)
                else:
                    print("<p><i>Please move or remove files from the directory"
                          "<br>before attempting to delete the category.</i>")
            print("<p>")
    print("Current categories:<br>")
    print(wt.new_form(sett['url'], 'post'))
    print(wt.put_form('hidden', 'm', 'c_del'))
    clist = catlist()
    for n, i in enumerate(clist):
        clist[n] = "<br>" + wt.put_form("checkbox", 'dir', i) \
                   + " /" + i \
                   + "/ (" + str(len(os.listdir(sett['dir'] + i))) + ")"
    print("\n".join(clist))
    print("<p>", wt.put_form('submit', 'del', 'Delete'))
    print("</form>")
    
    
def settings():
    if wt.get_form('sub'):
        change = 0
        for i in sett.keys():
            if wt.get_form(i) and wt.get_form(i) != sett[i].strip():
                change += 1
                sett[i] = wt.get_form(i)
                
        if change > 0:
            with open('sett.txt', 'w') as sett_txt:
                buff = []
                for i in sett.keys():
                    buff.append(str(i + " " + sett[i]))
                buff = '\n'.join(buff)
                sett_txt.write(buff)
            print("<p><b>Settings updated.</b>")
                
    print(wt.new_form(sett['url'], "post"),
          wt.put_form("hidden", "m", "settings"),
          "<table><tr><th colspan='3'>Admin settings",
          "<hr><i>Note: modify sett.txt if this gets messed up.</i>",
          "<tr><th>Setting<th>Current<th>Modify?")
    
    for i in sorted(sett.keys()):
        print("<tr><th>", i, "<td>", sett[i],
              "<td>", wt.put_form("text", i, sett[i]))
        
    print("<tr><th colspan='3'><br>",
          wt.put_form("submit", "sub", "Change"),
          "</table></form>")
    
def main():
    cookies = wt.get_cookie()
    pw = ''
    if os.path.isfile(sett['css']):
        css = sett['css']
    else:
        css = "admin.css"
        
    print(wt.head("admin panel"),
          "<link rel='stylesheet' type='text/css' href='{0}'>".format(css),
          "<body>")
    if 'pw' in cookies.keys():
        pw = cookies['pw']
    if pw == sett['pw']:
        panel()
        print(wt.get_ip())
    elif logged_in(wt.get_form("pw")):
        print(wt.put_cookie('pw', wt.get_form("pw")))
        panel()

main()
