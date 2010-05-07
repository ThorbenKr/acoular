import beamfpy
print beamfpy.__file__

from beamfpy import td_dir, L_p, TimeSamples, Calib, MicGeom, RectGrid, \
MaskedTimeSamples, FiltFiltOctave, Trajectory, BeamformerTimeSq, TimeAverage, \
TimeCache, FiltOctave, BeamformerTime, TimePower, BeamformerTimeSqTraj, \
WriteWAV
from numpy import empty, loadtxt, arange, where
from os import path
import sys

print sys.argv

if sys.argv[1]=='1':
    h5 = "2009-10-10_12-51-48_906000.h5"
    richtung = "lr"
elif sys.argv[1]=='2':
    h5 = "2009-10-10_12-56-33_187000.h5"
    richtung = "lr"
elif sys.argv[1]=='3':
    h5 = "2009-09-30_13-02-29_890000.h5"
    richtung = "rl"
traj = loadtxt(path.join(td_dir,path.splitext(h5)[0]+'.traj'))

tr = Trajectory()

bildfreq = 30.0
bild = 0
for bildnr,x,y,z in traj:
#    print x
    if ((-0.5 < x < 1.0) and richtung == "rl") or\
            ((-1.0 < x < 0.5) and richtung == "lr"):
        if bild==0:
            bild=int(bildnr)
        tr.points[(bildnr-bild)/bildfreq]=(-x,y,z-1.0)
        stopbild = int(bildnr)
        
print bild, stopbild, 2.0/((stopbild-bild)/bildfreq)

td=MaskedTimeSamples()
td.invalid_channels = arange(64,92,1).tolist()
c0 = 343.0
if sys.argv[2]=='92':
    m = MicGeom(from_file=path.join(td_dir,'array_92x_x3_9_y-1_7_mod.xml'))
m = MicGeom(from_file=path.join(td_dir,'array_64x_x3_9_y-1_7_mod.xml'))
g = RectGrid(x_min=-1,x_max=1.0,y_min=-1,y_max=1,z=1.0,increment=0.0625)
#~ g = RectGrid(x_min=-1,x_max=1.0,y_min=-1,y_max=1,z=0.0,increment=0.125)
#g = RectGrid(x_min=-2,x_max=2.0,y_min=-2,y_max=2,z=1.0,increment=0.25)
td.name=path.join(td_dir,h5)
cal=Calib(from_file=path.join(td_dir,'calib92x20091012_64-6_28-3_inverted.xml'))
td.calib = cal
td.start = (bild)*2048
td.stop= (stopbild)*2048
ww = WriteWAV(source = td)
#ww.channels = [70,84]
ww.channels = [0,]
ww.save()
fi = FiltFiltOctave(source = td)
fi.band = float(sys.argv[3])#4000
b = BeamformerTimeSqTraj(source = fi,grid=g, mpos=m, trajectory=tr)
#b = BeamformerTimeSq(source = fi,grid=g, mpos=m)
avg = TimeAverage(source = b)
avg.naverage=512
cach = TimeCache( source = avg)
r = empty((1,td.numsamples/avg.naverage,g.size))
k = 0
#for fi.band in (2000,):
#for fi.band in (500,1000,2000,):
#~ for fi.band in (1000,2000,4000,):
#~ for fi.band in (2000,4000,8000,):
j = 0
for i in cach.result(4):
    s = i.shape[0]
#    print r[k,j:j+s].shape,i.shape
    r[k,j:j+s] = i
    j += s
    print j
k += 1
#r=r[:,1:j]
#~ r[:,0]  = r.mean(1)
sh = g.shape

from pylab import *
print cach.sample_freq
fignr = 1
for res in r:
    f = figure(fignr)
    gtr = tr.traj(1/cach.sample_freq)
    a = f.add_subplot(5,6,30)
    map = L_p(res[:10].mean(axis=0))
    mx = map.max()
    mn = mx -10
    im = a.imshow(map.reshape(sh).T,vmin=mn,vmax=mx,extent=g.extend())
    colorbar(im,ax=a)
    plnr = 1
    for map in res:
        if plnr==5*6:
            break
        x,y,z = gtr.next()
        r2 = x*x + y*y + (z+1)*(z+1)
#        print x,y,z+1,sqrt(r2)
        a = f.add_subplot(5,6,plnr)
        mx1 = map.max()
#        map1 = where(map>mx1/10,map,0)
#        mx = 25
#        mn = mx-15
        mx1 = L_p(mx1)
        print x, sqrt(r2), mx1
        im = a.imshow(L_p(r2*map.reshape(sh).T),vmin=mn,vmax=mx,extent=g.extend())
        a.grid(b=True)
        plnr += 1
    fignr += 1
    

#f=figure()
#a=f.add_subplot(211)
#mx = r[0].max(-1).max()
#mn = mx-30#r[0].min()
#a.plot(clip(r[0].max(-1),mn,mx))
#im={}
#for k in range(3):
#    a=f.add_subplot(2,3,4+k)
#    mx = r[k].max()
#    mn = mx-20#r[0].min()
#    im[k] = a.imshow(r[k,0].reshape(sh).T,vmin=mn,vmax=mx,extent=g.extend())
#    a.grid(b=True)
#    colorbar(im[k],ax=a)
#def update(y):
#    kc = y.GetKeyCode()
#    if kc == wx.WXK_RIGHT:
#        update.i += 1
#    if kc == wx.WXK_LEFT:
#        update.i -= 1              
#    if update.i==r.shape[1]:
#        update.i=0
#    print update.i
#    for k in range(3):
#        im[k].set_array(r[k,update.i].reshape(sh).T)
#    f.canvas.draw()
#update.i=0
#import wx
#wx.EVT_KEY_DOWN(wx.GetApp(), update)
show()