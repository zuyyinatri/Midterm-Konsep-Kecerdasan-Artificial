import heapq, itertools, time, json

N=5;
PEGS="ABC";
GOAL=((),(),tuple(range(N,0,-1)));
START=(tuple(range(N,0,-1)),(),())
ORDER=[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]

def move_cost(model,d,a,b):
    if model=="unit": return 1
    if model=="size": return d          # W1: linear in disc size
    if model=="dist": return abs(a-b)   # W2: peg distance (A=0,B=1,C=2)
    raise ValueError

def successors(s,model):
    for a,b in ORDER:
        if not s[a]: continue
        d=s[a][-1]
        if s[b] and s[b][-1]<d: continue
        t=[list(x) for x in s]; t[a].pop(); t[b].append(d)
        yield (d,a,b),tuple(tuple(x) for x in t),move_cost(model,d,a,b)

def peg_of(s):
    p={}
    for i,pg in enumerate(s):
        for d in pg: p[d]=i
    return p

# ---- exact tower cost T(m, X->Y) for sub-problem with m discs
from functools import lru_cache
def tower_cost(model,m,x,y):
    if m==0: return 0
    st=tuple(tuple(range(m,0,-1)) if i==x else () for i in range(3))
    goal=tuple(tuple(range(m,0,-1)) if i==y else () for i in range(3))
    dist={st:0}; pq=[(0,0,st)]; c=itertools.count(1)
    while pq:
        g,_,s=heapq.heappop(pq)
        if g>dist[s]: continue
        if s==goal: return g
        for _,t,w in successors(s,model):
            if t not in dist or g+w<dist[t]:
                dist[t]=g+w; heapq.heappush(pq,(g+w,next(c),t))
@lru_cache(None)
def T(model,m,x,y): return tower_cost(model,m,x,y)

def h1(s,model):
    p=peg_of(s)
    if model=="size": return sum(d for d in p if p[d]!=2)
    if model=="dist": return sum(2-p[d] for d in p)
    return sum(1 for d in p if p[d]!=2)
def h2(s,model):
    p=peg_of(s); wrong=[d for d in p if p[d]!=2]
    if not wrong: return 0
    k=max(wrong)
    if model=="size": return k+T(model,k-1,0,2)          # k itself + tower(k-1) to C
    if model=="dist": return 1+min(T(model,k-1,0,2),T(model,k-1,1,2))
    return 2**(k-1)
HEUR={"h1":h1,"h2":h2}

def search(algo,model,hname=None):
    hf=(lambda s:HEUR[hname](s,model)) if hname else (lambda s:0)
    cnt=itertools.count()
    def key(g,depth,h):
        return {"BFS":(depth,),"UCS":(g,),"Greedy":(h,),"A*":(g+h,h)}[algo]
    pq=[(key(0,0,hf(START)),next(cnt),START,0,0,None,None)]
    open_g={START:0}; seen={START}; closed=set(); parent={}
    gen=1; maxf=1; exp=[]; 
    while pq:
        k,_,s,g,dep,par,mv=heapq.heappop(pq)
        if s in closed or (algo in("UCS","A*") and g>open_g.get(s,1e18)): continue
        fr=[(x,gx,hf(x)) for x,gx in open_g.items()] if len(exp)<14 else None
        open_g.pop(s,None); closed.add(s); parent[s]=(par,mv,g)
        exp.append(dict(state=s,g=g,h=hf(s),parent=par,move=mv,depth=dep,frontier=fr))
        if s==GOAL:
            path=[];x=s
            while parent[x][0] is not None:
                path.append(parent[x][1]); x=parent[x][0]
            path.reverse()
            return dict(path=path,cost=g,steps=len(path),expanded=len(exp),generated=gen,maxfrontier=maxf,exp=exp)
        for m,t,w in successors(s,model):
            g2=g+w
            if t in closed: continue
            if algo in("UCS","A*"):
                if t in open_g and open_g[t]<=g2: continue
            else:
                if t in seen: continue
            seen.add(t); open_g[t]=g2; gen+=1
            heapq.heappush(pq,(key(g2,dep+1,hf(t)),next(cnt),t,g2,dep+1,s,m))
            maxf=max(maxf,len(open_g))
    return None

def hstar(model):
    """exact cost-to-go by backward Dijkstra (graph is undirected w/ symmetric costs)"""
    dist={GOAL:0}; pq=[(0,0,GOAL)]; c=itertools.count(1)
    while pq:
        g,_,s=heapq.heappop(pq)
        if g>dist[s]: continue
        for _,t,w in successors(s,model):
            if t not in dist or g+w<dist[t]:
                dist[t]=g+w; heapq.heappush(pq,(g+w,next(c),t))
    return dist

def path_cost(path,model): return sum(move_cost(model,d,a,b) for d,a,b in path)
def fmt(path): return ", ".join(f"{d}{PEGS[a]}{PEGS[b]}" for d,a,b in path)

if __name__=="__main__":
    out={}
    for model in("unit","size","dist"):
        hs=hstar(model); assert len(hs)==3**N
        chk={}
        for hn in("h1","h2"):
            adm=all(HEUR[hn](s,model)<=hs[s] for s in hs)
            cons=all(HEUR[hn](s,model)<=w+HEUR[hn](t,model) for s in hs for _,t,w in successors(s,model))
            chk[hn]=dict(adm=adm,cons=cons,maxh=max(HEUR[hn](s,model) for s in hs),
                         tight=sum(HEUR[hn](s,model)==hs[s] for s in hs),
                         mean=sum(HEUR[hn](s,model) for s in hs)/len(hs))
        out[model]=dict(opt=hs[START],maxhstar=max(hs.values()),check=chk,runs={})
        print(model,"h*(start)=",hs[START],"max h*",max(hs.values()),chk)
        runs=[("BFS",None),("UCS",None),("Greedy","h1"),("A*","h1"),("Greedy","h2"),("A*","h2")]
        for algo,hn in runs:
            r=search(algo,model,hn)
            ts=[]
            for _ in range(200):
                t0=time.perf_counter(); search(algo,model,hn); ts.append(time.perf_counter()-t0)
            r["ms"]=1000*sum(ts)/len(ts)
            r["realcost"]=path_cost(r["path"],model)
            assert r["realcost"]==r["cost"]
            out[model]["runs"][f"{algo}|{hn}"]=r
            print(f"  {algo:7s}{str(hn):5s} steps={r['steps']} cost={r['cost']} exp={r['expanded']} gen={r['generated']} fr={r['maxfrontier']} ms={r['ms']:.2f}")
    import pickle; pickle.dump(out,open("res.pkl","wb"))
